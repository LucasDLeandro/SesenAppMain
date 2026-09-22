const CORPO_PADRAO = `Prezados, favor liberar o acesso para a seguinte equipe:

Empresa: {empresa}
Solicitante: {solicitante}
Período do Dia: {periodo}
Datas Autorizadas: {datas}

Técnicos Presentes:
{tecnicos}`;

const ASSINATURA_PADRAO = `Atenciosamente,
SesenApp`;

window.abrirModalNovoTemplate = function() {
    document.getElementById('form-template-acesso').reset();
    document.getElementById('template_id').value = '';
    document.getElementById('modalTemplateAcessoLabel').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Novo Template de Liberação';
    document.getElementById('template_ativo').checked = false;
    document.getElementById('template_assunto').value = '[SEGURANÇA] Liberação de Acesso de Terceiros';
    document.getElementById('template_corpo').value = CORPO_PADRAO;
    document.getElementById('template_assinatura').value = ASSINATURA_PADRAO;
}

window.editarTemplate = function(id, nome, assunto, destinatario, copia, corpo, assinatura, ativo) {
    document.getElementById('template_id').value = id;
    document.getElementById('template_nome').value = nome;
    document.getElementById('template_assunto').value = assunto;
    document.getElementById('template_destinatario').value = destinatario;
    document.getElementById('template_copia').value = copia;
    document.getElementById('template_corpo').value = corpo;
    document.getElementById('template_assinatura').value = assinatura;
    document.getElementById('template_ativo').checked = ativo;
    document.getElementById('modalTemplateAcessoLabel').innerHTML = '<i class="bi bi-pencil-square me-2"></i>Editar Template: ' + nome;
}
