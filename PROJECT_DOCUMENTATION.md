**Project Overview**

- **Name**: PythonProject1 (Knowledge Graph & Bayesian Network Pipeline)
- **Purpose**: A pipeline that extracts disease-symptom relationships from text, populates a Neo4j knowledge graph, and uses a Bayesian network to predict disease probabilities based on observed symptoms.
- **Main dependencies**: `neo4j` (Python driver), `spacy` (with `en_core_web_sm`), `pgmpy`, `pandas`.

**Files Summary**

- **`Final_Augmented_dataset_Diseases_and_Symptoms.csv`**: Raw dataset file.
  - **Format**: CSV with "diseases" column and one-hot encoded symptom columns (1 for present, 0 for absent).
  - **Content**: Large dataset of disease-symptom associations.

- **`Data_From_CSV.py`**: Dataset converter.
  - **Purpose**: processing `Final_Augmented_dataset_Diseases_and_Symptoms.csv` into the `knowledge.txt` format.
  - **Key behavior**:
    - Reads the CSV line by line.
    - Extracts the disease name and collects all symptoms marked with '1'.
    - writes unique entries to `knowledge.txt`.

- **`knowledge.txt`**: A plain-text knowledge base.
  - **Format**: "Disease has symptoms Symptom1, Symptom2, ..."
  - **Content**: Contains entries for various diseases (e.g., Flu, COVID-19, Malaria) and their associated symptoms. Can be manually edited or generated via `Data_From_CSV.py`.
  - **Usage**: Source data for `read_knowledge.py` and `graph_builder.py`.

- **`read_knowledge.py`**: Basic file I/O demonstration.
  - **Purpose**: Verifies that `knowledge.txt` exists and is readable.
  - **Key behavior**: Reads and prints each line of the knowledge base with its line number. Useful for a quick sanity check of the data file.

- **`neo4j_connect_test.py`**: Neo4j connectivity tester.
  - **Purpose**: Verifies that the application can connect to the Neo4j database using the provided credentials.
  - **Key behavior**:
    - Connects to Neo4j using environment variables or default local credentials.
    - Prints a success message if the connection is established, or an error message otherwise.
    - **Usage**: Run this before `graph_builder.py` to ensure the database is accessible.

- **`graph_builder.py`**: Knowledge Graph Population.
  - **Purpose**: Parses `knowledge.txt` and populates the Neo4j database with `Disease` and `Symptom` nodes and `HAS_SYMPTOM` relationships.
  - **Key behavior**:
    - **Configuration**: Uses environment variables (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`) with fallback defaults.
    - **NLP/Extraction**: Uses `spacy` (mostly for tokenization context, though core extraction is a deterministic string split on `" has symptoms "`).
    - **Graph Operations**:
      - Clears the existing database (`MATCH (n) DETACH DELETE n`) before population.
      - Uses `MERGE` to create `Disease` and `Symptom` nodes to avoid duplicates.
      - Creates `(Disease)-[:HAS_SYMPTOM]->(Symptom)` relationships.
  - **Output**: Prints the status of each processed line and extracted entities.

- **`bayesian_predictor.py`**: Bayesian Network Inference.
  - **Purpose**: Builds a Discrete Bayesian Network from the Neo4j graph data and performs disease prediction.
  - **Key behavior**:
    - **Data Fetching**: Queries Neo4j for all `(Disease)-[:HAS_SYMPTOM]->(Symptom)` relationships.
    - **Model Building**: Uses `pgmpy` to construct a Bayesian Network.
      - **Priors**: assigns uniform probability priors to diseases based on their frequency in the graph (which is usually 1 per disease).
      - **CPDs**: Implements a "noisy-OR" style conditional probability distribution for symptoms, allowing for multiple parent diseases.
    - **Inference**: Uses `VariableElimination` to predict the probability of diseases given a set of observed symptoms.
  - **Interactive Mode**: When run as a script, it prompts the user to enter symptoms and outputs the top predicted diseases.

**Configuration & Dependencies**

- **Neo4j Configuration**:
  - The scripts look for the following environment variables:
    - `NEO4J_URI`: Default `neo4j://127.0.0.1:7687`
    - `NEO4J_USER`: Required
    - `NEO4J_PASSWORD`: Required
    - `NEO4J_DATABASE`: Default `neo4j`

- **Python Dependencies**:
  - `neo4j`: Official Neo4j Python driver.
  - `spacy`: Industrial-strength NLP (requires `en_core_web_sm` model).
  - `pgmpy`: Probabilistic Graphical Models library.
  - `pandas`: Data manipulation (dependency of pgmpy).

- **`requirements.txt`**:
  Should contain:
  ```text
  neo4j
  spacy
  pgmpy
  pandas
  ```

**Quick Setup & Run**

1.  **Environment Setup**:
    ```bash
    # Create virtual environment
    python -m venv .venv
    
    # Activate virtual environment
    # Windows (PowerShell):
    .\.venv\Scripts\Activate.ps1
    # macOS/Linux:
    source .venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Download spaCy model
    python -m spacy download en_core_web_sm
    ```

2.  **Generate Knowledge Base** (Optional if knowledge.txt exists):
    ```bash
    python Data_From_CSV.py
    ```

3.  **Verify Data**:
    ```bash
    python read_knowledge.py
    ```

4.  **Test Database Connection**:
    ```bash
    python neo4j_connect_test.py
    ```

5.  **Populate Knowledge Graph**:
    *Warning: This will clear existing data in the configured Neo4j database.*
    ```bash
    python graph_builder.py
    ```

6.  **Run Disease Predictor**:
    ```bash
    python bayesian_predictor.py
    ```
    *Follow the on-screen prompts to enter symptoms (e.g., "Fever, Cough").*

**Notes**

- **Credentials**: It is recommended to set the `NEO4J_*` environment variables rather than relying on the hard-coded defaults in production.
- **Extraction**: The current extraction logic in `graph_builder.py` is strict (`split(" has symptoms ")`). Ensure `knowledge.txt` follows the exact format `Disease has symptoms Symptom1, Symptom2`.
- **Model Assumptions**: The Bayesian model uses simplified probability assumptions (uniform priors, noisy-OR) for demonstration purposes.
