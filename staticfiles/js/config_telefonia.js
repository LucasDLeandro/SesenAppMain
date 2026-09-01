let modalTemplate = null;
let modalTemplateTutorial = null;
let modalTemplateEmail = null;

document.addEventListener('DOMContentLoaded', function() {
    const mt = document.getElementById('modalTemplate');
    if (mt) modalTemplate = new bootstrap.Modal(mt);
    
    const mtt = document.getElementById('modalTemplateTutorial');
    if (mtt) modalTemplateTutorial = new bootstrap.Modal(mtt);
    
    const mte = document.getElementById('modalTemplateEmail');
    if (mte) modalTemplateEmail = new bootstrap.Modal(mte);
});

function novoTemplate() {
    document.getElementById('form-template').reset();
    document.getElementById('template_id').value = '';
    document.getElementById('modalTemplateLabel').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Novo Template';
    document.getElementById('ativo').checked = false;
    
    document.getElementById('cabecalho_logo').value = 'TSE';
    document.getElementById('cabecalho_sublogo').value = 'Tribunal Superior Eleitoral';
    document.getElementById('cabecalho_subtitulo').value = 'Secretaria de Administração | COSEN - SESEN';
    
    if(modalTemplate) modalTemplate.show();
}

function editarTemplate(id, nome, cab_logo, cab_sublogo, cab_subtit, instCel, instInter, instIntl, termObrig, termLonga, termRessar, isAtivo) {
    document.getElementById('template_id').value = id;
    document.getElementById('nome').value = nome;
    document.getElementById('cabecalho_logo').value = cab_logo;
    document.getElementById('cabecalho_sublogo').value = cab_sublogo;
    document.getElementById('cabecalho_subtitulo').value = cab_subtit;
    document.getElementById('instrucoes_celular').value = instCel;
    document.getElementById('instrucoes_interurbanas').value = instInter;
    document.getElementById('instrucoes_internacionais').value = instIntl;
    document.getElementById('termo_obrigatorio').value = termObrig;
    document.getElementById('termo_ligacoes_longa_distancia').value = termLonga;
    document.getElementById('termo_ressarcimento').value = termRessar;
    document.getElementById('ativo').checked = isAtivo;
    
    document.getElementById('modalTemplateLabel').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Editar Template #' + id;
    if(modalTemplate) modalTemplate.show();
}

function novoTemplateTutorial() {
    document.getElementById('form-template-tutorial').reset();
    document.getElementById('tutorial_template_id').value = '';
    document.getElementById('modalTemplateTutorialLabel').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Novo Template de Tutorial';
    document.getElementById('tutorial_ativo').checked = false;
    
    document.getElementById('tutorial_cabecalho_logo').value = 'TSE';
    document.getElementById('tutorial_cabecalho_sublogo').value = 'Tribunal Superior Eleitoral';
    document.getElementById('tutorial_cabecalho_subtitulo').value = 'Secretaria de Administração | COSEN - SESEN';
    
    if(modalTemplateTutorial) modalTemplateTutorial.show();
}

function editarTemplateTutorial(id, nome, cab_logo, cab_sublogo, cab_subtit, intro, exemplo, val, pag, cons, duv, isAtivo) {
    document.getElementById('tutorial_template_id').value = id;
    document.getElementById('tutorial_nome').value = nome;
    document.getElementById('tutorial_cabecalho_logo').value = cab_logo;
    document.getElementById('tutorial_cabecalho_sublogo').value = cab_sublogo;
    document.getElementById('tutorial_cabecalho_subtitulo').value = cab_subtit;
    
    document.getElementById('tutorial_introducao').value = intro;
    document.getElementById('tutorial_exemplo_email').value = exemplo;
    document.getElementById('tutorial_secao_validacao').value = val;
    document.getElementById('tutorial_secao_pagamento').value = pag;
    document.getElementById('tutorial_secao_consequencias').value = cons;
    document.getElementById('tutorial_secao_duvidas').value = duv;
    
    document.getElementById('tutorial_ativo').checked = isAtivo;
    
    document.getElementById('modalTemplateTutorialLabel').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Editar Template #' + id;
    if(modalTemplateTutorial) modalTemplateTutorial.show();
}

function novoTemplateEmail() {
    document.getElementById('form-template-email').reset();
    document.getElementById('email_template_id').value = '';
    document.getElementById('modalTemplateEmailLabel').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Novo Template de E-mail';
    document.getElementById('email_ativo').checked = false;
    
    document.getElementById('email_assunto').value = 'Senha Telefônica - SESEN';
    document.getElementById('email_copia').value = '';
    document.getElementById('email_assinatura').value = 'Seção de Equipamentos e Sistemas de Engenharia\nTelefone/Ramal: 61 3030-8224';
    
    if(modalTemplateEmail) modalTemplateEmail.show();
}

function editarTemplateEmail(id, nome, assunto, email_copia, corpo, assinatura, isAtivo) {
    document.getElementById('email_template_id').value = id;
    document.getElementById('email_nome').value = nome;
    document.getElementById('email_assunto').value = assunto;
    document.getElementById('email_copia').value = email_copia;
    document.getElementById('email_corpo').value = corpo;
    document.getElementById('email_assinatura').value = assinatura;
    document.getElementById('email_ativo').checked = isAtivo;
    
    document.getElementById('modalTemplateEmailLabel').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Editar Template de E-mail #' + id;
    if(modalTemplateEmail) modalTemplateEmail.show();
}
