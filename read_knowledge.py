# --- Configuration ---
# Make sure 'knowledge.txt' is in the same directory as this Python script
KNOWLEDGE_FILE = 'knowledge.txt'

print(f"Attempting to read from: {KNOWLEDGE_FILE}")

try:
    # 'with' statement ensures the file is automatically closed
    # 'r' mode is for reading
    # 'encoding='utf-8'' is good practice for text files to handle various characters
    with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines() # Reads all lines into a list of strings

        print(f"\nSuccessfully read {len(lines)} lines from '{KNOWLEDGE_FILE}':\n")

        # Iterate through each line and print it
        for i, line in enumerate(lines):
            # .strip() removes leading/trailing whitespace, including newline characters
            print(f"Line {i+1}: {line.strip()}")

except FileNotFoundError:
    print(f"ERROR: The file '{KNOWLEDGE_FILE}' was not found.")
    print("Please ensure 'knowledge.txt' is in the same directory as this script.")
except Exception as e:
    print(f"An unexpected error occurred while reading the file: {e}")

print("\nFinished reading knowledge base.")