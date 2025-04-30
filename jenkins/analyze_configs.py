import os
import sys
import time
import re

def suggest_updates(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        sys.exit(1)

    print(f"Analyzing {file_path}... (Simulating API Call)")
    time.sleep(1)

    filename = os.path.basename(file_path).lower()
    with open(file_path, 'r') as f:
        raw_lines = f.readlines()  # Preserve line numbers and spacing

    suggestions = []

    if 'outputs.conf' in filename:
        expected = [
            '[tcpout]',
            'defaultGroup = default-autolb-group',
            '[tcpout:default-autolb-group]',
            'server = 127.0.0.1:9997'
        ]
        current_lines = [line.strip() for line in raw_lines if line.strip()]
        if current_lines != expected:
            suggestions.append("Configuration mismatch detected in outputs.conf. Please ensure the standard tcpout settings.")
        else:
            suggestions.append("No suggestions found.")

    elif 'inputs.conf' in filename:
        stanza_start = None
        stanza_lines = []

        for i, line in enumerate(raw_lines):
            stripped = line.strip()
            if stripped.startswith('[') and stripped.endswith(']'):
                if stanza_lines:
                    suggestions += analyze_stanza(stanza_start + 1, stanza_lines)
                stanza_start = i
                stanza_lines = [stripped]
            elif stanza_lines is not None:
                stanza_lines.append(stripped)

        if stanza_lines:
            suggestions += analyze_stanza(stanza_start + 1, stanza_lines)

        if not suggestions:
            suggestions.append("No suggestions found.")
    else:
        suggestions.append("Unknown config file. No analysis performed.")

    return suggestions

def analyze_stanza(start_line, stanza_lines):
    missing = []

    if not any(re.match(r'^\s*index\s*=', line, re.IGNORECASE) for line in stanza_lines):
        missing.append("`index = your_index_name`")
    if not any(re.match(r'^\s*sourcetype\s*=', line, re.IGNORECASE) for line in stanza_lines):
        missing.append("`sourcetype = your_sourcetype`")
    if not any(re.match(r'^\s*disabled\s*=', line, re.IGNORECASE) for line in stanza_lines):
        missing.append("`disabled = true|false`")

    if missing:
        return [f"Stanza starting at line {start_line}: Missing {', '.join(missing)}"]
    return []

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python analyze_configs.py <path_to_conf_file>")
        sys.exit(1)

    suggestions = suggest_updates(sys.argv[1])
    for suggestion in suggestions:
        print(suggestion)
