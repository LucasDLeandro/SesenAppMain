import os

html_file = r"C:\Lucas\SesenAppMain\telefonia\templates\telefonia\modals\form_nada_consta_modal.html"

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
