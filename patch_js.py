import os

js_file = r"C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\modal_forms.js"

try:
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # Find the autocomplete listener to fill ramal and email
    target_js_1 = '''                                inputServidor.value = item.nome;
                                hiddenCpf.value = item.cpf || '';
                                hiddenMatricula.value = item.matricula || '';
                                autocompleteBox.style.display = 'none';'''
    replacement_js_1 = '''                                inputServidor.value = item.nome;
                                hiddenCpf.value = item.cpf || '';
                                hiddenMatricula.value = item.matricula || '';
                                if (document.getElementById('ramal_nada_consta')) document.getElementById('ramal_nada_consta').value = item.ramal || '';
                                if (document.getElementById('email_nada_consta')) document.getElementById('email_nada_consta').value = item.email || '';
                                autocompleteBox.style.display = 'none';'''

    # Fetch (Edit mode)
    target_js_2 = '''                    document.getElementById('servidor_nada_consta').value = data.servidor || '';
                    document.getElementById('hidden_cpf_nada_consta').value = data.cpf || '';
                    document.getElementById('hidden_matricula_nada_consta').value = data.matricula || '';'''
    replacement_js_2 = '''                    document.getElementById('servidor_nada_consta').value = data.servidor || '';
                    document.getElementById('hidden_cpf_nada_consta').value = data.cpf || '';
                    document.getElementById('hidden_matricula_nada_consta').value = data.matricula || '';
                    if (document.getElementById('ramal_nada_consta')) document.getElementById('ramal_nada_consta').value = data.ramal || '';
                    if (document.getElementById('email_nada_consta')) document.getElementById('email_nada_consta').value = data.email || '';'''

    # FormData (Save)
    target_js_3 = '''                servidor: document.getElementById('servidor_nada_consta').value,
                cpf: document.getElementById('hidden_cpf_nada_consta').value,
                matricula: document.getElementById('hidden_matricula_nada_consta').value,'''
    replacement_js_3 = '''                servidor: document.getElementById('servidor_nada_consta').value,
                cpf: document.getElementById('hidden_cpf_nada_consta').value,
                matricula: document.getElementById('hidden_matricula_nada_consta').value,
                ramal: document.getElementById('ramal_nada_consta') ? document.getElementById('ramal_nada_consta').value : '',
                email: document.getElementById('email_nada_consta') ? document.getElementById('email_nada_consta').value : '','''

    js_content = js_content.replace(target_js_1, replacement_js_1)
    js_content = js_content.replace(target_js_2, replacement_js_2)
    js_content = js_content.replace(target_js_3, replacement_js_3)
    
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("JS updated successfully")
except Exception as e:
    print(f"Error JS: {e}")
