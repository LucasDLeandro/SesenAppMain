import re

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all instances of <i class="fas fa-times"></i> with <i class="bi bi-x-lg"></i>
content = content.replace('<i class="fas fa-times"></i>', '<i class="bi bi-x-lg"></i>')

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Icons replaced!")
