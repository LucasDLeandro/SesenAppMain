import os
import re

js_file = r"C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js"
with open(js_file, 'r', encoding='utf-8') as f:
    js_content = f.read()

target_js = r"document.getElementById('hidden_matricula_nada_consta').value = data.matricula || '';"
replacement_js = r"document.getElementById('hidden_matricula_nada_consta').value = data.matricula || '';" + "\n              if (document.getElementById('ramal_nada_consta')) document.getElementById('ramal_nada_consta').value = data.ramal || '';\n              if (document.getElementById('email_nada_consta')) document.getElementById('email_nada_consta').value = data.email || '';"

js_content = js_content.replace(target_js, replacement_js)

with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)
print("Updated list_telefonia.js successfully")
