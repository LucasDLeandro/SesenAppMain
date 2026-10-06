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

    // ── Controle de visibilidade das variáveis por módulo ──
    function atualizarVariaveisVisiveis(tipoEvento) {
        var varsElev = document.getElementById('vars-elevadores');
        var varsTel  = document.getElementById('vars-telefonia');
        var varsTelAparelho     = document.getElementById('vars-tel-aparelho');
        var varsTelSenha        = document.getElementById('vars-tel-senha');
        var varsTelRecolhimento = document.getElementById('vars-tel-recolhimento');
        var varsTelNadaConsta   = document.getElementById('vars-tel-nada-consta');
        var varsTelNadaConstaConclusao = document.getElementById('vars-tel-nada-consta-conclusao');

        // Esconder tudo primeiro
        if (varsElev) varsElev.style.display = 'none';
        if (varsTel)  varsTel.style.display  = 'none';
        if (varsTelAparelho)     varsTelAparelho.style.display     = 'none';
        if (varsTelSenha)        varsTelSenha.style.display        = 'none';
        if (varsTelRecolhimento) varsTelRecolhimento.style.display = 'none';
        if (varsTelNadaConsta)   varsTelNadaConsta.style.display   = 'none';
        if (varsTelNadaConstaConclusao) varsTelNadaConstaConclusao.style.display = 'none';

        if (!tipoEvento || tipoEvento === 'false') return;

        // Elevadores: qualquer valor que comece com "os_elev_" ou "VAGO_"
        if (tipoEvento.startsWith('os_elev_') || tipoEvento.startsWith('VAGO_')) {
            if (varsElev) varsElev.style.display = 'block';
        }
        // Telefonia: qualquer valor que comece com "tel_"
        else if (tipoEvento.startsWith('tel_')) {
            if (varsTel) varsTel.style.display = 'block';

            // Exibir sub-bloco específico do tipo de telefonia
            if (tipoEvento === 'tel_solicitacao_aparelho') {
                if (varsTelAparelho) varsTelAparelho.style.display = 'block';
            } else if (tipoEvento === 'tel_solicitacao_senha') {
                if (varsTelSenha) varsTelSenha.style.display = 'block';
            } else if (tipoEvento === 'tel_recolhimento_evento') {
                if (varsTelRecolhimento) varsTelRecolhimento.style.display = 'block';
            } else if (tipoEvento === 'tel_nada_consta') {
                if (varsTelNadaConsta) varsTelNadaConsta.style.display = 'block';
            }
        }
    }

    // Listener de mudança no select de tipo_evento
    var tipoSelect = document.getElementById('id_tipo_evento');
    if (tipoSelect) {
        tipoSelect.addEventListener('change', function () {
            atualizarVariaveisVisiveis(this.value);
        });
    }

    // ── Botões "Novo Template" ──
    document.querySelectorAll('.btn-add-template').forEach(function (btn) {
        btn.addEventListener('click', function () {
            console.log("TEMPLATE_MODAL.JS - Botão Novo Template clicado!", btn);
            formEl.reset();
            if (hiddenId) hiddenId.value = '';
            formEl.action = urlCriar;

            // Pré-selecionar tipo de evento do módulo
            var defaultType = btn.getAttribute('data-default-type');
            var selectEl    = document.getElementById('id_tipo_evento');
            if (selectEl && defaultType) {
                for (var i = 0; i < selectEl.options.length; i++) {
                    if (selectEl.options[i].value === defaultType) {
                        selectEl.selectedIndex = i;
                        break;
                    }
                }
            }

            // Atualizar variáveis visíveis com base no tipo pré-selecionado
            atualizarVariaveisVisiveis(defaultType || (selectEl ? selectEl.value : ''));

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

        // Atualizar variáveis visíveis com base no tipo do template sendo editado
        atualizarVariaveisVisiveis(tipo_evento);

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
