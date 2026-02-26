# BayesianNetwork-Medical-Diagnosis-System

A Python pipeline for medical diagnosis experimentation using:
- a text knowledge base (`knowledge.txt`)
- a Neo4j knowledge graph (`Disease` and `Symptom` nodes)
- Bayesian inference (`pgmpy`) to predict likely diseases from observed symptoms

## Project Workflow

1. Convert CSV disease/symptom data into text facts.
2. Load text facts into Neo4j as a graph.
3. Build a Bayesian network from Neo4j relationships.
4. Query likely diseases from user-entered symptoms.

## Repository Structure

- `Final_Augmented_dataset_Diseases_and_Symptoms.csv`: Raw dataset (large CSV).
- `Data_From_CSV.py`: Creates `knowledge.txt` from the CSV.
- `knowledge.txt`: Text knowledge base in the format:
  - `Disease has symptoms Symptom1, Symptom2, ... .`
- `read_knowledge.py`: Reads and prints `knowledge.txt` for validation.
- `neo4j_connect_test.py`: Verifies Neo4j connectivity.
- `graph_builder.py`: Parses `knowledge.txt` and populates Neo4j.
- `bayesian_predictor.py`: Builds Bayesian network and runs interactive predictions.
- `PROJECT_DOCUMENTATION.md`: Extended project notes.

## Requirements

- Python 3.9+ (recommended)
- Neo4j database (local or remote)
- Python packages:
  - `neo4j`
  - `spacy`
  - `pgmpy`
  - `pandas`

Install dependencies:

```bash
pip install neo4j spacy pgmpy pandas
python -m spacy download en_core_web_sm
```

## Neo4j Configuration

Scripts use these environment variables (with defaults):

- `NEO4J_URI` (default: `neo4j://127.0.0.1:7687`)
- `NEO4J_USER` (required)
- `NEO4J_PASSWORD` (required)
- `NEO4J_DATABASE` (default: `neo4j`)

PowerShell example:

```powershell
$env:NEO4J_URI="neo4j://127.0.0.1:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="your_password"
$env:NEO4J_DATABASE="neo4j"
```

## Setup and Run

### 1) Create and activate virtual environment (optional, recommended)

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2) Generate `knowledge.txt` (optional)

If you already have `knowledge.txt`, skip this.

```bash
python Data_From_CSV.py
```

Note: `Data_From_CSV.py` randomly samples up to 200 rows from the CSV (`max_records = 200`).

### 3) Validate knowledge base

```bash
python read_knowledge.py
```

### 4) Test Neo4j connection

```bash
python neo4j_connect_test.py
```

### 5) Build Neo4j graph

```bash
python graph_builder.py
```

Warning: `graph_builder.py` clears existing data before loading (`MATCH (n) DETACH DELETE n`).

### 6) Run Bayesian predictor

```bash
python bayesian_predictor.py
```

Then enter comma-separated symptoms, for example:

```text
Fever, Cough, Headache
```

## Notes and Assumptions

- `graph_builder.py` expects lines in `knowledge.txt` to include the exact separator:
  - `" has symptoms "`
- Predictor uses simplified assumptions:
  - disease priors estimated from graph frequencies
  - symptom CPDs approximated with a noisy-OR approach
- Results are for educational/prototyping use and are not medical advice.

## Troubleshooting

- spaCy model error:
  - Run `python -m spacy download en_core_web_sm`
- Neo4j connection fails:
  - Check Neo4j is running, credentials are correct, and bolt URI/port is reachable
- No predictions returned:
  - Ensure graph was populated successfully and entered symptoms match available symptom names
