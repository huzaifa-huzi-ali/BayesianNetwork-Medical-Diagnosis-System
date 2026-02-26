import os
from neo4j import GraphDatabase

def main():
    uri = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
    user = os.getenv('NEO4J_USER')
    password = os.getenv('NEO4J_PASSWORD')
    if not user or not password:
        print('Error: Set NEO4J_USER and NEO4J_PASSWORD environment variables.')
        return
    print(f'Testing Neo4j connectivity to: {uri}  user: {user}')
    driver = None
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print('Connection successful.')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if driver:
            driver.close()

if __name__ == '__main__':
    main()
