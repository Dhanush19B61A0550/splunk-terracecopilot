import os
import sys
import time
import re

def suggest_updates(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        sys.exit(1)

    print(f"Analyzing {file_path}... (Simulating API Call)")
    time.sleep(2)

    with open(file_path, 'r') as f:
        lines = f.readlines()

    suggestions = []
    current_stanza = []
    stanza_start_line = 0
    inside_stanza = False

    for idx, line in enumerate(lines):
        stripped = line.strip()

        # If new monitor stanza starts
        if stripped.startswith('[monitor://'):
            if current_stanza:
                # analyze previous stanza
                stanza_text = ''.join(current_stanza)
                if 'index =' not in stanza_text:
                    suggestions.append(f"Stanza starting at line {stanza_start_line+1}: Missing `index = your_index_name`")
                current_stanza = []

            inside_stanza = True
            stanza_start_line = idx
            current_stanza.append(line)

        elif inside_stanza and (stripped == '' or stripped.startswith('[')):
            # End of stanza, analyze
            stanza_text = ''.join(current_stanza)
            if 'index =' not in stanza_text:
                suggestions.append(f"Stanza starting at line {stanza_start_line+1}: Missing `index = your_index_name`")
            current_stanza = []
            inside_stanza = False

            # if next line starts a new stanza, start collecting again
            if stripped.startswith('[monitor://'):
                inside_stanza = True
                stanza_start_line = idx
                current_stanza.append(line)

        elif inside_stanza:
            current_stanza.append(line)

    # analyze last stanza if any
    if current_stanza:
        stanza_text = ''.join(current_stanza)
        if 'index =' not in stanza_text:
            suggestions.append(f"Stanza starting at line {stanza_start_line+1}: Missing `index = your_index_name`")

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
