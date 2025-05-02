import os
import sys
import time
import re
import codecs

# Force Python to use UTF-8 encoding for stdout (Windows compatibility)
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def suggest_updates(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The file {file_path} does not exist.")
        sys.exit(1)

    print(f"Analyzing {file_path}... (Simulating API Call)")
    time.sleep(1)

    filename = os.path.basename(file_path).lower()
    with open(file_path, 'r') as f:
        raw_lines = f.readlines()  # Don't strip yet to keep line numbers accurate

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
            suggestions.append("❌ Configuration mismatch detected in outputs.conf. Please ensure the standard tcpout settings.")
        else:
            suggestions.append("✅ No issues found in outputs.conf.")

    elif 'inputs.conf' in filename:
        stanza_start_line = None
        stanza_lines = []

        for i, raw_line in enumerate(raw_lines):
            line = raw_line.strip()
            if not line:
                continue  # Skip empty lines

            if line.startswith('[') and line.endswith(']'):
                if stanza_lines:
                    suggestions += analyze_stanza(stanza_start_line, stanza_lines)
                stanza_start_line = i + 1  # Human-readable line number
                stanza_lines = [line]
            else:
                stanza_lines.append(line)

        # Don't forget the last stanza
        if stanza_lines:
            suggestions += analyze_stanza(stanza_start_line, stanza_lines)

        if not suggestions:
            suggestions.append("✅ No issues found in inputs.conf.")

    else:
        suggestions.append("⚠ Unknown config file. No analysis performed.")

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
        return [f"❌ Stanza starting at line {start_line}: Missing {', '.join(missing)} ⚠"]
    return [f"✅ Stanza starting at line {start_line}: All required keys are present."]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python analyze_configs.py <path_to_conf_file>")
        sys.exit(1)

    suggestions = suggest_updates(sys.argv[1])
    for suggestion in suggestions:
        print(suggestion)
