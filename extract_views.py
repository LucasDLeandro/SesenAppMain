import json
import re

transcript_path = r'c:\Users\lucas.leandro.adml\.gemini\antigravity-ide\brain\3ffa7ed8-e02a-4f3a-a6ad-4e6f1016671f\.system_generated\logs\transcript_full.jsonl'

lines_dict = {}

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'VIEW_FILE' and 'telefonia/views.py' in data.get('content', ''):
            content = data['content']
            # Regex to match `<line_number>: <original_line>`
            matches = re.findall(r'^(\d+): (.*)$', content, re.MULTILINE)
            for num_str, text in matches:
                num = int(num_str)
                lines_dict[num] = text
        
        # Also let's check CODE_ACTIONs just in case they have newer versions of lines
        if data.get('type') == 'CODE_ACTION' and 'c:\\Lucas\\SesenAppMain\\telefonia\\views.py' in data.get('content', ''):
            content = data['content']
            # Diff format is hard to parse line by line without context, but since we mostly viewed it, let's see how many lines we get.

# Write the recovered lines to a file
with open('c:\\Lucas\\SesenAppMain\\telefonia_views_recovered.py', 'w', encoding='utf-8') as out:
    for num in sorted(lines_dict.keys()):
        out.write(lines_dict[num] + '\n')
print(f"Recovered {len(lines_dict)} lines.")
