import os
import sys
import time
import re

# Emoji/symbol replacements
ERROR = "❌"
SUCCESS = "✅"
WARNING = "⚠️"
INFO = "ℹ️"

# Print suggestions
def print_suggestions(suggestions):
    print("\n--- Suggestions ---")
    for suggestion in suggestions:
        print(suggestion)

# Entry function
def suggest_updates(file_path):
    if not os.path.exists(file_path):
        print(f"{ERROR} Error: The file '{file_path}' does not exist.")
        sys.exit(1)

    print(f"{INFO} Analyzing '{file_path}'... (Simulating API Call)")
    time.sleep(1)

    filename = os.path.basename(file_path).lower()
    with open(file_path, 'r') as f:
        raw_lines = f.readlines()

    suggestions = []

    if 'outputs.conf' in filename:
        suggestions += analyze_outputs_conf(raw_lines)
    elif 'inputs.conf' in filename:
        suggestions += analyze_inputs_conf(raw_lines)
    else:
        suggestions.append(f"{WARNING} Unknown config file '{filename}'. No analysis performed.")

    if not suggestions:
        suggestions.append(f"{SUCCESS} No issues found in {filename}.")

    return suggestions

# Analyze inputs.conf logic
def analyze_inputs_conf(raw_lines):
    suggestions = []
    stanza_start_line = None
    stanza_lines = []

    for i, raw_line in enumerate(raw_lines):
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith('[') and line.endswith(']'):
            if stanza_lines:
                suggestions += analyze_stanza(stanza_start_line, stanza_lines)
            stanza_start_line = i + 1
            stanza_lines = [line]
        else:
            stanza_lines.append(line)

    # Analyze last stanza
    if stanza_lines:
        suggestions += analyze_stanza(stanza_start_line, stanza_lines)

    return suggestions

# Analyze outputs.conf logic
def analyze_outputs_conf(raw_lines):
    suggestions = []
    required_structure = [
        '[tcpout]',
        'defaultGroup = default-autolb-group',
        '[tcpout:default-autolb-group]',
        'server = 127.0.0.1:9997'
    ]

    current_lines = [line.strip() for line in raw_lines if line.strip()]
    mismatches = []

    for expected_line in required_structure:
        if expected_line not in current_lines:
            mismatches.append(expected_line)

    if mismatches:
        suggestions.append(f"{ERROR} outputs.conf is missing the following required settings:\n    - " + "\n    - ".join(mismatches))
    else:
        suggestions.append(f"{SUCCESS} outputs.conf configuration is valid.")

    return suggestions

# Analyze individual stanza
def analyze_stanza(start_line, stanza_lines):
    missing = []
    required_fields = ['index', 'sourcetype', 'disabled']

    for field in required_fields:
        if not any(re.match(rf'^\s*{field}\s*=\s*', line, re.IGNORECASE) for line in stanza_lines):
            missing.append(f"{field} = <value>")

    if missing:
        return [f"{ERROR} Stanza starting at line {start_line} is missing required fields:\n    - " + "\n    - ".join(missing)]
    
    return []

# Script entry point
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"{ERROR} Usage: python analyze_configs.py <path_to_conf_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    suggestions = suggest_updates(file_path)
    print_suggestions(suggestions)
