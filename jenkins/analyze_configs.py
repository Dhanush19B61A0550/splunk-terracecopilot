import os
import sys
import time
import re

# Emoji/symbol replacements
ERROR = "❌"
SUCCESS = "✅"
WARNING = "⚠️"
INFO = "ℹ️"

def print_suggestions(suggestions):
    """
    Print formatted list of suggestions.
    """
    print("\n--- Suggestions ---")
    for suggestion in suggestions:
        print(suggestion)

def suggest_updates(file_path):
    """
    Analyze the given .conf file and provide suggestions.
    """
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
        suggestions.extend(analyze_outputs_conf(raw_lines))
    elif 'inputs.conf' in filename:
        suggestions.extend(analyze_inputs_conf(raw_lines))
    else:
        suggestions.append(f"{WARNING} Unknown config file '{filename}'. No analysis performed.")

    if not suggestions:
        suggestions.append(f"{SUCCESS} No issues found in '{filename}'.")

    return suggestions

def analyze_inputs_conf(raw_lines):
    """
    Analyze an inputs.conf file stanza by stanza.
    """
    suggestions = []
    stanza_start_line = None
    stanza_lines = []

    for i, raw_line in enumerate(raw_lines):
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith('[') and line.endswith(']'):
            if stanza_lines:
                suggestions.extend(analyze_stanza(stanza_start_line, stanza_lines))
            stanza_start_line = i + 1
            stanza_lines = [line]
        else:
            stanza_lines.append(line)

    if stanza_lines:
        suggestions.extend(analyze_stanza(stanza_start_line, stanza_lines))

    return suggestions

def analyze_outputs_conf(raw_lines):
    """
    Check if outputs.conf contains the required structure.
    """
    suggestions = []
    required_structure = [
        '[tcpout]',
        'defaultGroup = default-autolb-group',
        '[tcpout:default-autolb-group]',
        'server = 127.0.0.1:9997'
    ]

    current_lines = [line.strip() for line in raw_lines if line.strip()]
    mismatches = [expected for expected in required_structure if expected not in current_lines]

    if mismatches:
        suggestions.append(
            f"{ERROR} 'outputs.conf' is missing the following required settings:\n    - " +
            "\n    - ".join(mismatches)
        )
    else:
        suggestions.append(f"{SUCCESS} 'outputs.conf' configuration is valid.")

    return suggestions

def analyze_stanza(start_line, stanza_lines):
    """
    Check if the stanza contains all required fields.
    """
    required_fields = ['index', 'sourcetype', 'disabled']
    missing_fields = []

    for field in required_fields:
        if not any(re.match(rf'^\s*{field}\s*=\s*', line, re.IGNORECASE) for line in stanza_lines):
            missing_fields.append(f"{field} = <value>")

    if missing_fields:
        return [
            f"{ERROR} Stanza starting at line {start_line} is missing required fields:\n    - " +
            "\n    - ".join(missing_fields)
        ]
    
    return []

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"{ERROR} Usage: python analyze_configs.py <path_to_conf_file>")
        sys.exit(1)

    config_file_path = sys.argv[1]
    results = suggest_updates(config_file_path)
    print_suggestions(results)
