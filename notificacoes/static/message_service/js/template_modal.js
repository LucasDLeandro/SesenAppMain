// FORMULÁRIO TEMPLATE MODAL
// Envolvido em DOMContentLoaded para garantir que os elementos do modal já existam no DOM
document.addEventListener('DOMContentLoaded', function() {
    const form_template = document.getElementById('template-form');
    if (!form_template) return; // Página não possui este modal

    //URLs
    const urlCriarTemplate = form_template.getAttribute('data-url-criar-template');
    const urlEditarTemplateBase = form_template.getAttribute('data-url-editar-template');

    // Expor função de update globalmente para ser chamada via onclick nos cards de template
    window.abrirModalTemplateUpdate = function(id, id_message, texto, status, tipo_evento) {
        console.log(tipo_evento)
        
        document.getElementById('id_oculto_template').value = id
        document.getElementById('id_id_template').value = id_message
        document.getElementById('id_base_text').value = texto
        document.getElementById('id_tipo_evento').value = tipo_evento
        
        const isAtivoEl = document.getElementById('id_is_ativo') || document.getElementById('id_template_is_ativo');
        if (isAtivoEl) {
            isAtivoEl.checked = (status === 'True');
        }

        const urlEditarTemplate = urlEditarTemplateBase.replace('/0/', `/${id}/`)
        form_template.action = urlEditarTemplate

        const modalInst = bootstrap.Modal.getOrCreateInstance(document.getElementById('templateModal'));
        modalInst.show();
    }

    // Submit do formulário de template
    form_template.addEventListener('submit', async function(evento) {
        evento.preventDefault();

        const urlDestino = form_template.action;
        const formData = new FormData(form_template);

        try {
            const resposta = await fetch(urlDestino, {
                method: 'POST',
                body: formData
            });

            const dados = await resposta.json();
            if (resposta.ok && dados.sucesso) {
                await Swal.fire({
                    title: "Ótima Notícia!",
                    text: "O template foi salvo com sucesso!",
                    icon: "success",
                    iconColor: "#3bfd00",
                    confirmButtonColor: "#0065fd"
                })
                const inst = bootstrap.Modal.getInstance(document.getElementById('templateModal'));
                if (inst) inst.hide();
                window.location.reload();
            } else {
                console.log(`Erros encontrados no formulário: ${dados.erros}`)
                Swal.fire("Erro!", "Não foi possível salvar. Verifique os dados inseridos.", "error")
            }
        } catch (erro) {
            console.error("Erro crítico na conexão: ", erro)
            Swal.fire("Falha!", "Erro ao conectar com o servidor. Tente novamente mais tarde.", "error")
        }
    })

    // Botões de deletar template
    const botoesDeletarTemplate = document.querySelectorAll('.btn-deletar-template')
    botoesDeletarTemplate.forEach(botao => {
        botao.addEventListener('click', async function() {
            const id_template = botao.getAttribute('data-del-template-id')
            const urlDestinoBase = botao.getAttribute('data-url-del-template')
            const urlDestinoFinal = urlDestinoBase.replace('/0/', `/${id_template}/`)

            const result = await Swal.fire({
                title: "Você tem certeza?",
                text: "Você não conseguirá reverter essa ação depois!",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Sim, deletar!",
                cancelButtonText: "Cancelar"
            })

            if (result.isConfirmed) {
                try {
                    const resposta = await fetch(urlDestinoFinal, {
                        method:'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    })

                    const dados = await resposta.json()

                    if (resposta.ok && dados.sucesso) {
                        await Swal.fire({
                            title: "Deletado!",
                            text: "O template foi deletado!",
                            icon: "success"
                        })
                        window.location.reload();
                    } else {
                        Swal.fire("Erro!", "Não foi possível deletar o template no servidor.", "error")
                    }

                } catch (erro) {
                    console.error("Erro crítico na conexão:", erro)
                    Swal.fire("Falha!", "Erro ao conectar com o servidor. Tente novamente mais tarde.", "error")
                }
            }
        })
    })
});
