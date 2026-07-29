/**
 * contato_modal.js
 * Gerencia o modal de criação/edição/exclusão de Contatos de Notificação.
 * Toda a lógica é executada apenas após o DOM estar pronto.
 */
document.addEventListener('DOMContentLoaded', function () {
    console.log("CONTATO_MODAL.JS - Iniciando script...");

    // ── Elementos ──
    var modalEl = document.getElementById('contatoModal');
    var formEl  = document.getElementById('contato-form');

    console.log("CONTATO_MODAL.JS - modalEl:", modalEl, "formEl:", formEl);

    // Se a página não possui este modal, abortar silenciosamente
    if (!modalEl || !formEl) {
        console.warn("CONTATO_MODAL.JS - Elementos não encontrados. Abortando.");
        return;
    }

    // Move o modal para a raiz do body para evitar bugs de z-index e CSS overflow clipping
    document.body.appendChild(modalEl);

    var modal          = new bootstrap.Modal(modalEl);
    var urlCriar       = formEl.getAttribute('data-url-criar-contato');
    var urlEditarBase  = formEl.getAttribute('data-url-editar-contato');
    var hiddenId       = document.getElementById('id_oculto_contato');

    // ── Botões "Adicionar Contato" ──
    document.querySelectorAll('.btn-add-contato').forEach(function (btn) {
        btn.addEventListener('click', function () {
            console.log("CONTATO_MODAL.JS - Botão Adicionar Contato clicado!", btn);
            formEl.reset();
            if (hiddenId) hiddenId.value = '';
            formEl.action = urlCriar;

            // Pré-marcar checkbox do módulo correspondente
            var modulo    = btn.getAttribute('data-modulo');
            var checkElev = document.getElementById('id_notifica_elevadores');
            var checkTel  = document.getElementById('id_notifica_telefonia');

            if (checkElev && checkTel) {
                checkElev.checked = (modulo === 'elevadores');
                checkTel.checked  = (modulo === 'telefonia');
            }

            modal.show();
        });
    });

    // ── Abrir para edição (chamado via onclick na tabela) ──
    window.abrirModalContatoUpdate = function (id, nome, telefone, email, role, notif_elevadores, notif_telefonia, rec_whatsapp, rec_email, status) {
        if (hiddenId) hiddenId.value = id;

        var elNome     = document.getElementById('id_nome');
        var elTelefone = document.getElementById('id_telefone');
        var elEmail    = document.getElementById('id_email');
        var elRole     = document.getElementById('id_role');

        if (elNome)     elNome.value     = nome;
        if (elTelefone) elTelefone.value = telefone;
        if (elEmail)    elEmail.value    = email || '';
        if (elRole)     elRole.value     = role;

        // Checkboxes booleanos
        var setCheck = function (elId, val) {
            var el = document.getElementById(elId);
            if (el) el.checked = (val === 'True');
        };
        setCheck('id_notifica_elevadores', notif_elevadores);
        setCheck('id_notifica_telefonia', notif_telefonia);
        setCheck('id_receber_whatsapp', rec_whatsapp);
        setCheck('id_receber_email', rec_email);
        setCheck('id_contato_is_ativo', status);

        formEl.action = urlEditarBase.replace('/0/', '/' + id + '/');
        modal.show();
    };

    // ── Submit do formulário ──
    formEl.addEventListener('submit', async function (e) {
        e.preventDefault();

        try {
            var resposta = await fetch(formEl.action, {
                method: 'POST',
                body: new FormData(formEl)
            });
            var dados = await resposta.json();

            if (resposta.ok && dados.sucesso) {
                await Swal.fire({
                    title: 'Ótima Notícia!',
                    text: 'O contato foi salvo com sucesso!',
                    icon: 'success',
                    iconColor: '#3bfd00',
                    confirmButtonColor: '#0065fd'
                });
                modal.hide();
                window.location.reload();
            } else {
                Swal.fire('Erro!', 'Há um problema com o formulário, verifique os dados.', 'error');
            }
        } catch (erro) {
            console.error('Erro na conexão:', erro);
            Swal.fire('Falha!', 'Erro ao conectar com o servidor.', 'error');
        }
    });

    // ── Botões de deletar contato ──
    document.querySelectorAll('.btn-deletar-contato').forEach(function (botao) {
        botao.addEventListener('click', async function () {
            var id  = botao.getAttribute('data-del-contato-id');
            var url = botao.getAttribute('data-url-del-contato').replace('/0/', '/' + id + '/');

            var result = await Swal.fire({
                title: 'Você tem certeza?',
                text: 'Você não conseguirá reverter essa ação depois!',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sim, deletar!',
                cancelButtonText: 'Cancelar'
            });

            if (result.isConfirmed) {
                try {
                    var resposta = await fetch(url, {
                        method: 'POST',
                        headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
                    });
                    var dados = await resposta.json();

                    if (resposta.ok && dados.sucesso) {
                        await Swal.fire({ title: 'Deletado!', text: 'O contato foi deletado!', icon: 'success' });
                        window.location.reload();
                    } else {
                        Swal.fire('Erro!', 'Não foi possível deletar o contato.', 'error');
                    }
                } catch (erro) {
                    console.error('Erro na conexão:', erro);
                    Swal.fire('Falha!', 'Erro ao conectar com o servidor.', 'error');
                }
            }
        });
    });

    // ── Máscara de telefone ──
    var telInput = document.getElementById('id_telefone');
    if (telInput && typeof IMask !== 'undefined') {
        IMask(telInput, { mask: '(00) 0 0000-0000' });
    }
});
