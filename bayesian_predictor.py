import os
from neo4j import GraphDatabase
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from itertools import product


NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


def fetch_disease_symptom_data():
    driver = None
    records = []
    try:
        if not NEO4J_USER or not NEO4J_PASSWORD:
            print("Error: Set NEO4J_USER and NEO4J_PASSWORD environment variables.")
            return records
        driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD), database=NEO4J_DATABASE
        )
        driver.verify_connectivity()
        query = """
        MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
        RETURN d.name AS Disease, s.name AS Symptom
        """
        with driver.session() as session:
            result = session.run(query)
            for record in result:
                records.append(record.data())
    except Exception as e:
        print(f"Neo4j Error: {e}")
    finally:
        if driver:
            driver.close()
    return records


def build_bayesian_network(records, max_parents=5):
    if not records:
        print("No data available.")
        return None, [], []

    # Filter out invalid or self-loop edges
    edges = [(r['Disease'], r['Symptom']) for r in records
             if r['Disease'] and r['Symptom'] and r['Disease'] != r['Symptom']]

    # --- Count co-occurrences of disease-symptom pairs ---
    symptom_co_occurrence = {}
    for d, s in edges:
        symptom_co_occurrence.setdefault(s, {})
        symptom_co_occurrence[s][d] = symptom_co_occurrence[s].get(d, 0) + 1

    # --- Select top N most frequent parents for each symptom ---
    filtered_symptom_parents = {}
    final_edges = []
    for symptom, parent_counts in symptom_co_occurrence.items():
        # Sort parents by frequency and pick top N
        top_parents = sorted(parent_counts, key=parent_counts.get, reverse=True)[:max_parents]
        filtered_symptom_parents[symptom] = top_parents
        for p in top_parents:
            final_edges.append((p, symptom))

    # --- Create Bayesian Network ---
    model = DiscreteBayesianNetwork(final_edges)
    all_diseases = list({d for d, _ in final_edges})
    all_symptoms = list({s for _, s in final_edges})

    # --- Disease priors ---
    disease_counts = {d: 0 for d in all_diseases}
    for d, _ in edges:
        if d in disease_counts:
            disease_counts[d] += 1
    total = sum(disease_counts.values())
    for d in all_diseases:
        prob_true = disease_counts[d] / total
        cpd = TabularCPD(variable=d, variable_card=2,
                         values=[[1 - prob_true], [prob_true]])
        model.add_cpds(cpd)

    # --- Symptom CPDs (Noisy-OR) ---
    base_prob = 0.05
    added_cpds = set()
    for symptom, parents in filtered_symptom_parents.items():
        num_parents = len(parents)
        if num_parents == 0:
            if symptom not in added_cpds:
                cpd = TabularCPD(variable=symptom, variable_card=2,
                                 values=[[1 - base_prob], [base_prob]])
                model.add_cpds(cpd)
                added_cpds.add(symptom)
            continue

        # Compute parent probabilities based on co-occurrence frequency
        parent_probs = []
        for p in parents:
            count = sum(1 for d, s_ in edges if d == p and s_ == symptom)
            parent_prob = count / disease_counts[p] if disease_counts[p] else 0.6
            parent_probs.append(parent_prob)

        # Noisy-OR CPD table
        values_true, values_false = [], []
        for combo in product([0, 1], repeat=num_parents):
            prob_false = 1.0
            for i, state in enumerate(combo):
                if state == 1:
                    prob_false *= (1 - parent_probs[i])
            if all(state == 0 for state in combo):
                prob_false *= (1 - base_prob)
            prob_true = 1 - prob_false
            values_true.append(prob_true)
            values_false.append(1 - prob_true)

        if symptom not in added_cpds:
            cpd = TabularCPD(
                variable=symptom,
                variable_card=2,
                values=[values_false, values_true],
                evidence=parents,
                evidence_card=[2] * num_parents
            )
            model.add_cpds(cpd)
            added_cpds.add(symptom)

    try:
        model.check_model()
    except ValueError as e:
        print(f"Error: {e}")
        return None, [], []

    return model, all_diseases, all_symptoms



def filter_relevant_diseases(records, observed_symptoms, min_overlap=1):
    disease_map = {}
    for r in records:
        disease_map.setdefault(r['Disease'], set()).add(r['Symptom'])
    return [d for d, syms in disease_map.items()
            if len(syms.intersection(observed_symptoms)) >= min_overlap]


def predict_disease(model, diseases, all_symptoms, observed_symptoms, top_n=3):
    inference = VariableElimination(model)
    evidence = {s: 1 for s in observed_symptoms}

    results = {}
    for d in diseases:
        q = inference.query(variables=[d], evidence=evidence)
        idx = q.state_names[d].index(1)
        results[d] = q.values[idx]

    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:top_n])


if __name__ == "__main__":
    records = fetch_disease_symptom_data()
    model, all_diseases, all_symptoms = build_bayesian_network(records)
    if not model:
        exit()

    print("\nAvailable Symptoms:")
    print(", ".join(sorted(all_symptoms)))

    user_input = input("\nEnter symptoms (comma-separated): ").strip()
    if not user_input:
        exit()

    observed = [s.strip() for s in user_input.split(',') if s.strip()]
    invalid = [s for s in observed if s not in all_symptoms]
    if invalid:
        print(f"Invalid symptoms entered: {invalid}")
        exit()

    relevant_diseases = filter_relevant_diseases(records, set(observed), min_overlap=1)
    
    # Filter out diseases that are not in the Bayesian Network
    relevant_diseases = [d for d in relevant_diseases if d in all_diseases]

    if not relevant_diseases:
        print("No relevant diseases found in the model.")
        exit()

    predicted = predict_disease(model, relevant_diseases, all_symptoms, observed, top_n=3)
    print("\n--- Top Disease Predictions ---")
    for d, p in predicted.items():
        print(f"{d}: {p:.4f}")
