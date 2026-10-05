import os

js_file = r"C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\nada_consta.js"

try:
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # Fetch (Edit mode)
    target_js_2 = '''                    document.getElementById('nadaConstaCpf').value = data.cpf || '';
                    document.getElementById('nadaConstaMatricula').value = data.matricula || '';'''
    replacement_js_2 = '''                    document.getElementById('nadaConstaCpf').value = data.cpf || '';
                    document.getElementById('nadaConstaMatricula').value = data.matricula || '';
                    if (document.getElementById('nadaConstaRamal')) document.getElementById('nadaConstaRamal').value = data.ramal || '';
                    if (document.getElementById('nadaConstaEmail')) document.getElementById('nadaConstaEmail').value = data.email || '';'''

    # FormData (Save)
    target_js_3 = '''            cpf: document.getElementById('nadaConstaCpf').value,
            matricula: document.getElementById('nadaConstaMatricula').value,'''
    replacement_js_3 = '''            cpf: document.getElementById('nadaConstaCpf').value,
            matricula: document.getElementById('nadaConstaMatricula').value,
            ramal: document.getElementById('nadaConstaRamal') ? document.getElementById('nadaConstaRamal').value : '',
            email: document.getElementById('nadaConstaEmail') ? document.getElementById('nadaConstaEmail').value : '','''

    # Autocomplete
    target_js_1 = '''                            cpfInput.value = item.cpf || '';
                            matriculaInput.value = item.matricula || '';'''
    replacement_js_1 = '''                            cpfInput.value = item.cpf || '';
                            matriculaInput.value = item.matricula || '';
                            if (document.getElementById('nadaConstaRamal')) document.getElementById('nadaConstaRamal').value = item.ramal || '';
                            if (document.getElementById('nadaConstaEmail')) document.getElementById('nadaConstaEmail').value = item.email || '';'''

    if target_js_2 in js_content:
        js_content = js_content.replace(target_js_1, replacement_js_1)
        js_content = js_content.replace(target_js_2, replacement_js_2)
        js_content = js_content.replace(target_js_3, replacement_js_3)
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print("JS file updated successfully!")
    else:
        print("JS file target not found or already updated.")
except Exception as e:
    print(f"Error JS: {e}")
