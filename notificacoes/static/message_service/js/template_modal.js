// FORMULÁRIO TEMPLATE MODAL
const modal_template = new bootstrap.Modal(document.getElementById('templateModal'));
const form_template = document.getElementById('template-form')

//URLs
urlCriarTemplate = form_template.getAttribute('data-url-criar-template');
urlEditarTemplateBase = form_template.getAttribute('data-url-editar-template');

//Monitorar Evento de Clique em NOVO TEMPLATE
const btn_novo_template = document.getElementById('btn-novo-template')
btn_novo_template.addEventListener("click", abrirModalTemplateCreate)

function abrirModalTemplateCreate() {
    form_template.reset();

    id_oculto_template = document.getElementById('id_oculto_template');
    id_oculto_template.value = "";

    form_template.action = urlCriarTemplate

    console.log(`ID oculto: ${id_oculto_template.value}`)
    console.log(`urlCriar: ${form_template.action}`)
    
    modal_template.show();
}

function abrirModalTemplateUpdate(id, id_message, texto, status, tipo_evento) {
    console.log(tipo_evento)
    
    document.getElementById('id_oculto_template').value = id
    document.getElementById('id_id_template').value = id_message
    document.getElementById('id_base_text').value = texto

    if (status === "False") {
        document.getElementById('id_template_is_ativo').checked = false
    }

    document.getElementById('id_tipo_evento').value = tipo_evento

    const urlEditarTemplateReal = urlEditarTemplateBase.replace('/0/', `/${id}/`)
    form_template.action = urlEditarTemplateReal

    modal_template.show()
}

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
                title: "ótima Notícia!",
                text: "O template foi salvo com sucesso!",
                icon: "success",
                iconColor: "#3bfd00",
                confirmButtonColor: "#0065fd"
            })
            modal_template.hide();
            window.location.reload();
        } else {
            console.log(`Erros encontratos no formulário: ${dados.erros}`)
            alert("Não foi possível salvar. Verifique os dados inseridos")
        }
    } catch (erro) {
        console.error("Erro crítico na conexão: ", erro)
        alert("Erro ao conectar com o servidor. Tente novamente mais tarde.")
    }
})

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
                    Swal.fire({
                        title: "Deletado!",
                        text: "O template foi deletado!",
                        icon: "success"
                    })
                    document.getElementById(`card-template-${id_template}`)
                } else {
                    Swal.fire("Erro!", "Não foi possível deletar o contato no servidor.", "error")
                }

            } catch (erro) {
                console.error("Erro crítico na conexão:", erro)
                Swal.fire("Falha!", "Erro ao conectar com o servidor. Tente novamente mais tarde.", "error")
            }
        }
    })
})




