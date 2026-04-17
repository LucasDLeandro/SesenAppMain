//FORMULÁRIO CONTATO MODAL
const modal_contato = new bootstrap.Modal(document.getElementById('contatoModal'));
const form_contato = document.getElementById('contato-form');

//URLs 
const urlCriarContato = form_contato.getAttribute('data-url-criar-contato');
const urlEditarContatoBase = form_contato.getAttribute('data-url-editar-contato');

//Monitorar Evento de clique em NOVO CONTATO
const btn_novo_contato = document.getElementById('btn-novo-contato')
btn_novo_contato.addEventListener("click", abrirModalContatoCreate)

function abrirModalContatoCreate() {
    form_contato.reset();

    id_oculto = document.getElementById('id_oculto_contato');
    id_oculto.value = "";

    form_contato.action = urlCriarContato


    console.log(`ID oculto: ${id_oculto.value}`)
    console.log(`urlCriar: ${form_contato.action}`)
    
    modal_contato.show();
}

//

function abrirModalContatoUpdate(id, nome, telefone, role, status) {
    document.getElementById('id_oculto_contato').value = id
    document.getElementById('id_nome').value = nome
    document.getElementById('id_telefone').value = telefone
    document.getElementById('id_role').value = role
    

    if (status === "False")
        document.getElementById('id_contato_is_ativo').checked = false

    const urlEditarContatoReal = urlEditarContatoBase.replace('/0/', `/${id}/`)
    form_contato.action = urlEditarContatoReal

    modal_contato.show()
    
}

form_contato.addEventListener('submit', async function(evento) {
    evento.preventDefault();

    const urlDestino = form_contato.action;
    const formData = new FormData(form_contato);

    try {
        const resposta = await fetch(urlDestino, {
            method: 'POST',
            body: formData
        });

        const dados = await resposta.json();
        if (resposta.ok && dados.sucesso) {
            await Swal.fire({
                title: "Ótima Notícia!",
                text: "O contato foi salvo com sucesso!",
                icon: "success",
                iconColor: "#3bfd00",
                confirmButtonColor: "#0065fd"
            })
            modal_contato.hide();
            window.location.reload();
        } else {
            console.log(`Erros encontrados no formulário: ${dados.erros}`)
            Swal.fire("Erro!", "Há um problema com o formulário, verifique os dados.", "error")
        }
    } catch (erro) {
        console.error("Erro crítico na conexão:", erro)
        alert("Erro ao conectar com o servidor. Tente novamente mais tarde.")
    }
});



const botoesDeletarContato = document.querySelectorAll('.btn-deletar-contato')
botoesDeletarContato.forEach(botao => {
    botao.addEventListener('click', async function() {
        const id_contato = botao.getAttribute('data-del-contato-id')
        const urlDestinoBase = botao.getAttribute('data-url-del-contato')
        const urlDestinoFinal = urlDestinoBase.replace('/0/', `/${id_contato}/`)
        
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
        
        if (result.isConfirmed){
            try {
                const resposta = await fetch(urlDestinoFinal, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                const dados = await resposta.json()

                if (resposta.ok && dados.sucesso) {
                    Swal.fire({
                        title: "Deletado!",
                        text: "O contato foi deletado!",
                        icon: "success"
                    })
                    document.getElementById(`card-contato-${id_contato}`).remove()
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

IMask(
    document.getElementById('id_telefone'),
    {
        mask: '55 ',
        lazy: false
    }
)









