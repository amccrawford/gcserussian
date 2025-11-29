import csv
import json
import os

def convert_csv_to_json(csv_file_path, json_file_path):
    """
    Converts a CSV file with format [English],[Russian],[Category] to a JSON file.
    Each row in the CSV becomes a JSON object in a list.
    """
    vocabulary_list = []
    
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at '{csv_file_path}'")
        return

    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            for i, row in enumerate(csv_reader):
                if len(row) == 3:
                    vocabulary_list.append({
                        "english": row[0].strip(),
                        "russian": row[1].strip(),
                        "category": row[2].strip()
                    })
                else:
                    print(f"Warning: Skipping row {i+1} due to incorrect format (expected 3 columns, got {len(row)}): {row}")

        with open(json_file_path, mode='w', encoding='utf-8') as json_file:
            json.dump(vocabulary_list, json_file, ensure_ascii=False, indent=4)
        
        print(f"Successfully converted '{csv_file_path}' to '{json_file_path}'.")

    except Exception as e:
        print(f"An error occurred during conversion: {e}")

if __name__ == "__main__":
    csv_input_file = "vocab.csv"
    json_output_file = "vocab.json"

    # Create a dummy vocab.csv for testing if it doesn't exist
    if not os.path.exists(csv_input_file):
        print(f"Creating a dummy '{csv_input_file}' for demonstration.")
        dummy_content = [
            ["hello", "привет", "greeting"],
            ["goodbye", "до свидания", "greeting"],
            ["cat", "кошка", "animal"],
            ["dog", "собака", "animal"],
            ["thank you", "спасибо", "politeness"]
        ]
        with open(csv_input_file, mode='w', encoding='utf-8', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows(dummy_content)
        print("Dummy vocab.csv created. Run the script again to convert it.")
    else:
        convert_csv_to_json(csv_input_file, json_output_file)
