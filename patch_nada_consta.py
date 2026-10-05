import os

html_file = r"C:\Lucas\SesenAppMain\telefonia\templates\telefonia\includes\form_nada_consta_modal.html"
js_file = r"C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\form_nada_consta_modal.js"

# 1. Update HTML
try:
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    target_html = '''<div class="col-md-12">
                  <label for="servidor_nada_consta" class="form-label text-muted fw-bold text-uppercase mb-1">Nome do Servidor <span class="text-danger">*</span></label>
                  <input type="text" class="form-control format-text shadow-none" id="servidor_nada_consta" name="servidor" maxlength="200" required autocomplete="off" placeholder="Digite para buscar vnculos no sistema..." style="border-radius: 4px; border-color: var(--border-color);">
                  
                  <!-- Dropdown flutuante para resultados da busca -->
                  <div id="autocomplete-resultados" class="list-group shadow-sm position-absolute w-100" style="display: none; z-index: 1050; max-height: 200px; overflow-y: auto;">
                    <!-- Itens inseridos via JS -->
                  </div>
                </div>'''

    target_html2 = '''<div class="col-md-12">
                  <label for="servidor_nada_consta" class="form-label text-muted fw-bold text-uppercase mb-1">Nome do Servidor <span class="text-danger">*</span></label>
                  <input type="text" class="form-control format-text shadow-none" id="servidor_nada_consta" name="servidor" maxlength="200" required autocomplete="off" placeholder="Digite para buscar vnculos no sistema..." style="border-radius: 4px; border-color: var(--border-color);">
                  
                  <!-- Dropdown flutuante para resultados da busca -->
                  <div id="autocomplete-resultados" class="list-group shadow-sm position-absolute w-100" style="display: none; z-index: 1050; max-height: 200px; overflow-y: auto;">
                    <!-- Itens inseridos via JS -->
                  </div>
                </div>'''

    target_html3 = '''<div class="col-md-12">
                  <label for="servidor_nada_consta" class="form-label text-muted fw-bold text-uppercase mb-1">Nome do Servidor <span class="text-danger">*</span></label>
                  <input type="text" class="form-control format-text shadow-none" id="servidor_nada_consta" name="servidor" maxlength="200" required autocomplete="off" placeholder="Digite para buscar vínculos no sistema..." style="border-radius: 4px; border-color: var(--border-color);">
                  
                  <!-- Dropdown flutuante para resultados da busca -->
                  <div id="autocomplete-resultados" class="list-group shadow-sm position-absolute w-100" style="display: none; z-index: 1050; max-height: 200px; overflow-y: auto;">
                    <!-- Itens inseridos via JS -->
                  </div>
                </div>'''

    replacement_html = '''<div class="col-md-12">
                  <label for="servidor_nada_consta" class="form-label text-muted fw-bold text-uppercase mb-1">Nome do Servidor <span class="text-danger">*</span></label>
                  <input type="text" class="form-control format-text shadow-none" id="servidor_nada_consta" name="servidor" maxlength="200" required autocomplete="off" placeholder="Digite para buscar vínculos no sistema..." style="border-radius: 4px; border-color: var(--border-color);">
                  
                  <!-- Dropdown flutuante para resultados da busca -->
                  <div id="autocomplete-resultados" class="list-group shadow-sm position-absolute w-100" style="display: none; z-index: 1050; max-height: 200px; overflow-y: auto;">
                    <!-- Itens inseridos via JS -->
                  </div>
                </div>
                <div class="col-md-6 mt-3">
                    <label for="ramal_nada_consta" class="form-label text-muted fw-bold text-uppercase mb-1">Ramal de Contato</label>
                    <input type="text" class="form-control format-text shadow-none" id="ramal_nada_consta" name="ramal" maxlength="50" style="border-radius: 4px; border-color: var(--border-color);">
                </div>
                <div class="col-md-6 mt-3">
                    <label for="email_nada_consta" class="form-label text-muted fw-bold text-uppercase mb-1">E-mail do Servidor</label>
                    <input type="email" class="form-control shadow-none" id="email_nada_consta" name="email" maxlength="254" style="border-radius: 4px; border-color: var(--border-color);">
                </div>'''

    if target_html in html_content:
        html_content = html_content.replace(target_html, replacement_html)
    elif target_html2 in html_content:
        html_content = html_content.replace(target_html2, replacement_html)
    elif target_html3 in html_content:
        html_content = html_content.replace(target_html3, replacement_html)

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("HTML updated successfully")
except Exception as e:
    print(f"Error HTML: {e}")


# 2. Update JS
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
