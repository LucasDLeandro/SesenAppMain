import os

js_file = r"C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js"

try:
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    target_js = '''              document.getElementById('servidor_nada_consta').value = data.servidor || '';
              document.getElementById('hidden_cpf_nada_consta').value = data.cpf || '';
              document.getElementById('hidden_matricula_nada_consta').value = data.matricula || '';'''
    replacement_js = '''              document.getElementById('servidor_nada_consta').value = data.servidor || '';
              document.getElementById('hidden_cpf_nada_consta').value = data.cpf || '';
              document.getElementById('hidden_matricula_nada_consta').value = data.matricula || '';
              if (document.getElementById('ramal_nada_consta')) document.getElementById('ramal_nada_consta').value = data.ramal || '';
              if (document.getElementById('email_nada_consta')) document.getElementById('email_nada_consta').value = data.email || '';'''

    if target_js in js_content:
        js_content = js_content.replace(target_js, replacement_js)
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print("JS list_telefonia.js updated successfully")
    else:
        print("Target not found in list_telefonia.js")
except Exception as e:
    print(f"Error JS: {e}")
