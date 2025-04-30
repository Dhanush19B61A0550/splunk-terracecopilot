import os
import sys
import time
import re

# Emoji/symbol replacements
ERROR = "❌"
SUCCESS = "✅"
WARNING = "⚠️"

# Helper function to print suggestions
def print_suggestions(suggestions):
    for suggestion in suggestions:
        print(suggestion)

def suggest_updates(file_path):
    if not os.path.exists(file_path):
        print(f"{ERROR} Error: The file {file_path} does not exist.")
        sys.exit(1)

    print(f"{WARNING} Analyzing {file_path}... (Simulating API Call)")
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
        suggestions.append(f"{WARNING} Unknown config file. No analysis performed.")

    if not suggestions:
        suggestions.append(f"{SUCCESS} No suggestions found.")

    return suggestions

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

    if stanza_lines:
        suggestions += analyze_stanza(stanza_start_line, stanza_lines)

    return suggestions

def analyze_outputs_conf(raw_lines):
    suggestions = []
    expected = [
        '[tcpout]',
        'defaultGroup = default-autolb-group',
        '[tcpout:default-autolb-group]',
        'server = 127.0.0.1:9997'
    ]
    current_lines = [line.strip() for line in raw_lines if line.strip()]

    if current_lines != expected:
        suggestions.append(f"{ERROR} Configuration mismatch detected in outputs.conf. Please ensure the standard tcpout settings.")
    else:
        suggestions.append(f"{SUCCESS} Outputs.conf configuration is correct.")

    return suggestions

def analyze_stanza(start_line, stanza_lines):
    missing = []

    if not any(re.match(r'^\s*index\s*=\s*', line, re.IGNORECASE) for line in stanza_lines):
        missing.append("index = your_index_name")
    if not any(re.match(r'^\s*sourcetype\s*=\s*', line, re.IGNORECASE) for line in stanza_lines):
        missing.append("sourcetype = your_sourcetype")
    if not any(re.match(r'^\s*disabled\s*=\s*', line, re.IGNORECASE) for line in stanza_lines):
        missing.append("disabled = true|false")

    if missing:
        return [f"{ERROR} Stanza starting at line {start_line}: Missing {', '.join(missing)}"]
    return []

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"{ERROR} Usage: python analyze_configs.py <path_to_conf_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    suggestions = suggest_updates(file_path)
    print_suggestions(suggestions)
