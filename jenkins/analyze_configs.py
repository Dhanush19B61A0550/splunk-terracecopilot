import os
import sys
import time
import re
from colorama import init

# Initialize colorama
init(autoreset=True)

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Helper function to print suggestions
def print_suggestions(suggestions):
    for suggestion in suggestions:
        print(suggestion)

def suggest_updates(file_path):
    if not os.path.exists(file_path):
        print(f"{RED}Error: The file {file_path} does not exist.{RESET}")
        sys.exit(1)

    print(f"{YELLOW}Analyzing {file_path}... (Simulating API Call){RESET}")
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
        suggestions.append(f"{YELLOW}Unknown config file. No analysis performed.{RESET}")

    if not suggestions:
        suggestions.append(f"{GREEN}No suggestions found.{RESET}")

    return suggestions

# Analyze inputs.conf file
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

# Analyze outputs.conf file
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
        suggestions.append(f"{RED}Configuration mismatch detected in outputs.conf. Please ensure the standard tcpout settings.{RESET}")
    else:
        suggestions.append(f"{GREEN}No suggestions found.{RESET}")

    return suggestions

# Analyze a stanza inside the configuration files
def analyze_stanza(start_line, stanza_lines):
    missing = []

    if not any(re.match(r'^\s*index\s*=', line, re.IGNORECASE) for line in stanza_lines):
        missing.append("index = your_index_name")
    if not any(re.match(r'^\s*sourcetype\s*=', line, re.IGNORECASE) for line in stanza_lines):
        missing.append("sourcetype = your_sourcetype")
    if not any(re.match(r'^\s*disabled\s*=', line, re.IGNORECASE) for line in stanza_lines):
        missing.append("disabled = true|false")

    if missing:
        return [f"{RED}Stanza starting at line {start_line}: Missing {', '.join(missing)}{RESET}"]
    return []

# Main function to drive the script
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"{RED}Usage: python analyze_configs.py <path_to_conf_file>{RESET}")
        sys.exit(1)

    file_path = sys.argv[1]
    suggestions = suggest_updates(file_path)
    print_suggestions(suggestions)
