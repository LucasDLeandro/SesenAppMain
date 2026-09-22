let modalTemplate = null;

document.addEventListener('DOMContentLoaded', function() {
    const el = document.getElementById('modalTemplate');
    if (el) {
        modalTemplate = new bootstrap.Modal(el);
    }
});

function novoTemplate() {
    document.getElementById('form-template').reset();
    document.getElementById('template_id').value = '';
    document.getElementById('modalTemplateLabel').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Novo Template de Tutorial';
    document.getElementById('ativo').checked = false;
    
    // Default values for header
    document.getElementById('cabecalho_logo').value = 'TSE';
    document.getElementById('cabecalho_sublogo').value = 'Tribunal Superior Eleitoral';
    document.getElementById('cabecalho_subtitulo').value = 'Secretaria de Administração | COSEN - SESEN';
    
    if(modalTemplate) modalTemplate.show();
}

function editarTemplate(id, nome, cab_logo, cab_sublogo, cab_subtit, intro, exemplo, val, pag, cons, duv, isAtivo) {
    document.getElementById('template_id').value = id;
    document.getElementById('nome').value = nome;
    document.getElementById('cabecalho_logo').value = cab_logo;
    document.getElementById('cabecalho_sublogo').value = cab_sublogo;
    document.getElementById('cabecalho_subtitulo').value = cab_subtit;
    
    document.getElementById('introducao').value = intro;
    document.getElementById('exemplo_email').value = exemplo;
    document.getElementById('secao_validacao').value = val;
    document.getElementById('secao_pagamento').value = pag;
    document.getElementById('secao_consequencias').value = cons;
    document.getElementById('secao_duvidas').value = duv;
    
    document.getElementById('ativo').checked = isAtivo;
    
    document.getElementById('modalTemplateLabel').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Editar Template #' + id;
    if(modalTemplate) modalTemplate.show();
}
