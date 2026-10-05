import os

base_dir = r"C:\Lucas\SesenAppMain\telefonia\templates\telefonia\modals"
html_file = os.path.join(base_dir, "form_nada_consta.html")

js_file = r"C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\nada_consta.js"

# 1. Update HTML File
try:
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    target_html = '''<div class="col-md-6">
                                    <label class="form-label fw-bold text-secondary small">MATRÍCULA</label>
                                    <input type="text" name="matricula" id="nadaConstaMatricula" class="form-control">
                                </div>'''

    replacement_html = '''<div class="col-md-6">
                                    <label class="form-label fw-bold text-secondary small">MATRÍCULA</label>
                                    <input type="text" name="matricula" id="nadaConstaMatricula" class="form-control">
                                </div>
                                <div class="col-md-6 mt-3">
                                    <label class="form-label fw-bold text-secondary small">RAMAL DO SERVIDOR</label>
                                    <input type="text" name="ramal" id="nadaConstaRamal" class="form-control">
                                </div>
                                <div class="col-md-6 mt-3">
                                    <label class="form-label fw-bold text-secondary small">E-MAIL DO SERVIDOR</label>
                                    <input type="email" name="email" id="nadaConstaEmail" class="form-control">
                                </div>'''

    if target_html in html_content:
        html_content = html_content.replace(target_html, replacement_html)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("HTML file updated successfully!")
    else:
        print("HTML file target not found or already updated.")
except Exception as e:
    print(f"Error HTML: {e}")

# 2. Update JS File
try:
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # Find the autocomplete listener to fill ramal and email if available
    # Wait, does the API return ramal and email? Yes, probably. Let's add them to the input
    target_js_1 = '''                            cpfInput.value = item.cpf || '';
                            matriculaInput.value = item.matricula || '';'''
    replacement_js_1 = '''                            cpfInput.value = item.cpf || '';
                            matriculaInput.value = item.matricula || '';
                            if (document.getElementById('nadaConstaRamal')) document.getElementById('nadaConstaRamal').value = item.ramal || '';
                            if (document.getElementById('nadaConstaEmail')) document.getElementById('nadaConstaEmail').value = item.email || '';'''

    # Fetch (Edit mode)
    target_js_2 = '''                    document.getElementById('nadaConstaCpf').value = data.cpf || '';
                    document.getElementById('nadaConstaMatricula').value = data.matricula || '';'''
    replacement_js_2 = '''                    document.getElementById('nadaConstaCpf').value = data.cpf || '';
                    document.getElementById('nadaConstaMatricula').value = data.matricula || '';
                    document.getElementById('nadaConstaRamal').value = data.ramal || '';
                    document.getElementById('nadaConstaEmail').value = data.email || '';'''

    # FormData (Save)
    target_js_3 = '''            cpf: document.getElementById('nadaConstaCpf').value,
            matricula: document.getElementById('nadaConstaMatricula').value,'''
    replacement_js_3 = '''            cpf: document.getElementById('nadaConstaCpf').value,
            matricula: document.getElementById('nadaConstaMatricula').value,
            ramal: document.getElementById('nadaConstaRamal').value,
            email: document.getElementById('nadaConstaEmail').value,'''

    if target_js_1 in js_content:
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
