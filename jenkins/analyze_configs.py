import os
import sys
import time

def suggest_updates(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        sys.exit(1)

    print(f"Analyzing {file_path}... (Simulating API Call)")
    time.sleep(2)

    with open(file_path, 'r') as f:
        content = f.readlines()

    suggestions = []
    for idx, line in enumerate(content):
        # Check if the index line exists and is not empty
        if 'index = ' not in line or not line.strip().startswith('index = '):
            suggestions.append(f"Line {idx+1}: Suggest adding an `index = your_index_name` line")

        # Check for the 'disabled = false' that is not commented
        if 'disabled = false' in line and not line.strip().startswith('#'):
            suggestions.append(f"Line {idx+1}: Suggest enabling `disabled = true` for unused monitors")

    if not suggestions:
        suggestions.append("No suggestions found.")
    
    return suggestions

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python analyze_configs.py <path_to_conf_file>")
        sys.exit(1)

    suggestions = suggest_updates(sys.argv[1])
    for suggestion in suggestions:
        print(suggestion)
