import re

with open('elevadores/templates/ordens/includes/modais_mpm.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'<!-- Modal Cadastro MPM -->.*?<div class="modal fade modal-ordens-wrapper" id="modalCadastroMPM".*?</div>\n    </div>\n  </div>\n</div>', content, re.DOTALL)
if match:
    cad_modal = match.group(0)
    edit_modal = cad_modal.replace('modalCadastroMPM', 'modalEditarMPM')
    edit_modal = edit_modal.replace('Registrar Relatório de Manutenção Preventiva', 'Editar Relatório de Manutenção Preventiva')
    edit_modal = edit_modal.replace('formCadastroMPM', 'formEditarMPM')
    edit_modal = edit_modal.replace('id="mpm', 'id="editMpm')
    edit_modal = edit_modal.replace('for="mpm', 'for="editMpm')
    edit_modal = edit_modal.replace('Registrar Relatório MPM', 'Salvar Alterações')
    edit_modal = edit_modal.replace('<!-- Modal Cadastro MPM -->', '<!-- Modal Editar MPM -->')
    edit_modal = edit_modal.replace('<form id="formEditarMPM" enctype="multipart/form-data">', '<form id="formEditarMPM" enctype="multipart/form-data">\n            <input type="hidden" id="editMpmId" name="id">')

    with open('elevadores/templates/ordens/includes/modais_mpm.html', 'a', encoding='utf-8') as f:
        f.write('\n\n' + edit_modal + '\n')
    print('Modal appended successfully.')
else:
    print('Could not find modal match.')
