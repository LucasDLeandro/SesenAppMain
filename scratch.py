import os

file_path = 'c:/Lucas/SesenAppMain/telefonia/templates/telefonia/modals/form_nada_consta.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''<div class="col-md-6">
                                    <label class="form-label fw-bold text-secondary small">MATRÍCULA</label>
                                    <input type="text" name="matricula" id="nadaConstaMatricula" class="form-control">
                                </div>'''

replacement = '''<div class="col-md-6">
                                    <label class="form-label fw-bold text-secondary small">MATRÍCULA</label>
                                    <input type="text" name="matricula" id="nadaConstaMatricula" class="form-control">
                                </div>
                                <div class="col-md-6 mt-3">
                                    <label class="form-label fw-bold text-secondary small">RAMAL DE CONTATO</label>
                                    <input type="text" name="ramal" id="nadaConstaRamal" class="form-control">
                                </div>
                                <div class="col-md-6 mt-3">
                                    <label class="form-label fw-bold text-secondary small">E-MAIL DO SERVIDOR</label>
                                    <input type="email" name="email" id="nadaConstaEmail" class="form-control">
                                </div>'''

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Sucesso!")
else:
    print("Target não encontrado!")
