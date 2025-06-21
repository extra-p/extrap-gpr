import argparse
import json
import sys

# Keys to extract from the first input file
KEYS_TO_EXTRACT = [
    "percentage_bucket_counter_random",
    "mean_budget_random",
    "mean_add_points_random",
    "nr_func_modeled_random",
]

def read_json_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found -> {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {path}: {e}")
        sys.exit(1)

def write_json_file(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Output written to {path}")
    except Exception as e:
        print(f"Error writing to {path}: {e}")
        sys.exit(1)

def extract_keys(data, keys):
    return {key: data.get(key, None) for key in keys}

def main():
    parser = argparse.ArgumentParser(description='Extract keys from file1, combine with file2, and write output.')
    parser.add_argument('input_file_1', help='Path to the first input JSON file (specific keys extracted)')
    parser.add_argument('input_file_2', help='Path to the second input JSON file (all keys included)')
    parser.add_argument('output_file', help='Path to the output JSON file')

    args = parser.parse_args()

    data1 = read_json_file(args.input_file_1)
    data2 = read_json_file(args.input_file_2)
    data3 = {k: v for k, v in data2.items() if "random" not in k}

    extracted_data1 = extract_keys(data1, KEYS_TO_EXTRACT)

    # Combine into a single dictionary
    combined_data = {**extracted_data1, **data3}

    write_json_file(args.output_file, combined_data)

if __name__ == '__main__':
    main()

