import csv
import random

input_csv = "Final_Augmented_dataset_Diseases_and_Symptoms.csv"
output_txt = "knowledge.txt"
max_records = 200  


with open(input_csv, encoding="utf-8") as infile:
    reader = list(csv.DictReader(infile))  


sampled_rows = random.sample(reader, min(max_records, len(reader)))

with open(output_txt, "w", encoding="utf-8") as outfile:
    for row in sampled_rows:
        disease = row.get("diseases")
        symptoms = []

        
        for key, val in row.items():
            if key == "diseases":
                continue
            if val and val.strip() == "1":
                symptoms.append(key)

        if disease and symptoms:
            outfile.write(f"{disease} has symptoms {', '.join(symptoms)}.\n")

print(f"{len(sampled_rows)} diseases exported to {output_txt}")
