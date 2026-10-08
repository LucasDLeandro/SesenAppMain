import re

with open(r'C:\Lucas\SesenAppMain\telefonia\templates\telefonia\main_telefonia.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('list_telefonia.js\' %}?v=1.26', 'list_telefonia.js\' %}?v=1.27')

with open(r'C:\Lucas\SesenAppMain\telefonia\templates\telefonia\main_telefonia.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("HTML Version Bumped!")
