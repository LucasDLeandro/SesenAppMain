/**
 * template_modal.js
 * Gerencia o modal de criação/edição/exclusão de Templates de Notificação.
 * Toda a lógica é executada apenas após o DOM estar pronto.
 */
document.addEventListener('DOMContentLoaded', function () {
    console.log("TEMPLATE_MODAL.JS - Iniciando script...");

    // ── Elementos ──
    const modalEl = document.getElementById('templateModal');
    const formEl  = document.getElementById('template-form');

    console.log("TEMPLATE_MODAL.JS - modalEl:", modalEl, "formEl:", formEl);

    // Se a página não possui este modal, abortar silenciosamente
    if (!modalEl || !formEl) {
        console.warn("TEMPLATE_MODAL.JS - Elementos não encontrados. Abortando.");
        return;
    }

    // Move o modal para a raiz do body para evitar bugs de z-index e CSS overflow clipping
    document.body.appendChild(modalEl);

    const modal            = new bootstrap.Modal(modalEl);
    const urlCriar         = formEl.getAttribute('data-url-criar-template');
    const urlEditarBase    = formEl.getAttribute('data-url-editar-template');
    const hiddenId         = document.getElementById('id_oculto_template');

    // ── Botões "Novo Template" ──
    document.querySelectorAll('.btn-add-template').forEach(function (btn) {
        btn.addEventListener('click', function () {
            console.log("TEMPLATE_MODAL.JS - Botão Novo Template clicado!", btn);
            formEl.reset();
            if (hiddenId) hiddenId.value = '';
            formEl.action = urlCriar;

            // Pré-selecionar tipo de evento do módulo
            var defaultType = btn.getAttribute('data-default-type');
            var tipoSelect  = document.getElementById('id_tipo_evento');
            if (tipoSelect && defaultType) {
                for (var i = 0; i < tipoSelect.options.length; i++) {
                    if (tipoSelect.options[i].value === defaultType) {
                        tipoSelect.selectedIndex = i;
                        break;
                    }
                }
            }

            modal.show();
        });
    });

    // ── Abrir para edição (chamado via onclick nos cards) ──
    window.abrirModalTemplateUpdate = function (id, id_message, texto, status, tipo_evento) {
        if (hiddenId) hiddenId.value = id;

        var elIdTemplate = document.getElementById('id_id_template');
        var elBaseText   = document.getElementById('id_base_text');
        var elTipoEvento = document.getElementById('id_tipo_evento');
        var elIsAtivo    = document.getElementById('id_is_ativo') || document.getElementById('id_template_is_ativo');

        if (elIdTemplate) elIdTemplate.value = id_message;
        if (elBaseText)   elBaseText.value   = texto;
        if (elTipoEvento) elTipoEvento.value = tipo_evento;
        if (elIsAtivo)    elIsAtivo.checked  = (status === 'True');

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
                    text: 'O template foi salvo com sucesso!',
                    icon: 'success',
                    iconColor: '#3bfd00',
                    confirmButtonColor: '#0065fd'
                });
                modal.hide();
                window.location.reload();
            } else {
                Swal.fire('Erro!', 'Não foi possível salvar. Verifique os dados inseridos.', 'error');
            }
        } catch (erro) {
            console.error('Erro na conexão:', erro);
            Swal.fire('Falha!', 'Erro ao conectar com o servidor.', 'error');
        }
    });

    // ── Botões de deletar template ──
    document.querySelectorAll('.btn-deletar-template').forEach(function (botao) {
        botao.addEventListener('click', async function () {
            var id  = botao.getAttribute('data-del-template-id');
            var url = botao.getAttribute('data-url-del-template').replace('/0/', '/' + id + '/');

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
                        await Swal.fire({ title: 'Deletado!', text: 'O template foi deletado!', icon: 'success' });
                        window.location.reload();
                    } else {
                        Swal.fire('Erro!', 'Não foi possível deletar o template.', 'error');
                    }
                } catch (erro) {
                    console.error('Erro na conexão:', erro);
                    Swal.fire('Falha!', 'Erro ao conectar com o servidor.', 'error');
                }
            }
        });
    });
});
