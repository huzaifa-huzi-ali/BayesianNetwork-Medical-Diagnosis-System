import os
import spacy
from neo4j import GraphDatabase

# --- Neo4j Configuration (use environment variables when possible) ---
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")   

# --- Load spaCy NLP model ---
try:
    nlp = spacy.load("en_core_web_sm")
    print("spaCy model 'en_core_web_sm' loaded successfully.")
except Exception as e:
    print(f"Error loading spaCy model: {e}")
    print("Please ensure you ran 'python -m spacy download en_core_web_sm' in your PyCharm terminal.")
    exit() # Exit if NLP model can't be loaded

# --- Function to connect to Neo4j and add data ---
def create_graph_from_knowledge_base(knowledge_file='knowledge.txt'):
    driver = None
    try:
        if not NEO4J_USER or not NEO4J_PASSWORD:
            print("Error: Set NEO4J_USER and NEO4J_PASSWORD environment variables.")
            return
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD), database=NEO4J_DATABASE)
        driver.verify_connectivity()
        print("Successfully connected to Neo4j for graph population!")

        # Clear existing data to start fresh (useful for development)
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n") # DETACH DELETE removes relationships first, then nodes
            print("Existing data in Neo4j cleared before population.")

        # Read knowledge base and populate graph
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue # Skip empty lines

                print(f"--- Processing line {i+1}: '{line}' ---")
                doc = nlp(line) # Process the line with spaCy

                disease_name = None
                symptom_names = []

                # --- Entity Extraction Logic (from Task 4) ---
                parts = line.split(" has symptoms ", 1) # Split only on the first occurrence
                if len(parts) == 2: # Check if the split was successful
                    disease_name = parts[0].strip().replace('.', '')
                    symptom_list_str = parts[1].strip().replace('.', '')

                    symptom_names = [s.strip() for s in symptom_list_str.split(',')]
                    symptom_names = [s for s in symptom_names if s]

                if disease_name and symptom_names:
                    print(f"  Extracted Disease: '{disease_name}'")
                    print(f"  Extracted Symptoms: {symptom_names}")
                    # --- Graph Population Logic (Task 5 core) ---
                    with driver.session() as session:
                        # MERGE creates if not exists, matches if exists
                        session.run("MERGE (d:Disease {name: $disease_name})", disease_name=disease_name)
                        for symptom in symptom_names:
                            session.run("MERGE (s:Symptom {name: $symptom_name})", symptom_name=symptom)
                            # Create a HAS_SYMPTOM relationship
                            session.run("""
                                MATCH (d:Disease {name: $disease_name})
                                MATCH (s:Symptom {name: $symptom_name})
                                MERGE (d)-[:HAS_SYMPTOM]->(s)
                            """, disease_name=disease_name, symptom_name=symptom)
                    print(f"  Added '{disease_name}' and its symptoms to Neo4j.")
                else:
                    print(f"  WARNING: Could not reliably extract Disease and Symptoms from: '{line}'")

    except Exception as e:
        print(f"Error during graph population: {e}")
    finally:
        if driver:
            driver.close()
            print("Neo4j connection closed after graph population.")

# --- Main execution block for this script ---
if __name__ == "__main__":
    # Ensure knowledge.txt is in the same directory as this script
    create_graph_from_knowledge_base('knowledge.txt')
