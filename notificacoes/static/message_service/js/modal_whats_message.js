//FORMULÁRIO MODAL
const modal_contato = new bootstrap.Modal(document.getElementById('contatoModal'))
const form = document.getElementById('contato-form')

//URLs 
urlCriar = form.getAttribute('data-url-criar')
urlEditarBase = form.getAttribute('data-url-editar')



//Monitorar Evento de clique em NOVO CONTATO
const btn_novo_contato = document.getElementById('btn-novo-contato')
btn_novo_contato.addEventListener("click", abrirModalCreate)

function abrirModalCreate() {
    form.reset();

    id_oculto = document.getElementById('id_oculto');
    id_oculto.value = "";

    form.action = urlCriar

    console.log(`ID oculto: ${id_oculto.value}`)
    console.log(`urlCriar: ${urlCriar}`)
    
    modal_contato.show()
}

//

function abrirModalUpdate(id, nome, telefone, role, status) {
    document.getElementById('id_oculto').value = id
    document.getElementById('id_nome').value = nome
    document.getElementById('id_telefone').value = telefone
    document.getElementById('id_role').value = role
    document.getElementById('id_oculto').value = status

    const urlEditarReal = urlEditarBase.replace('/0/', `/${id}/`)
    form.action = urlEditarReal

    modal_contato.show()
}

form.addEventListener('submit', async function(evento) {
    evento.preventDefault();

    const urlDestino = form.action;
    const formData = new FormData(form)

    try {
        const resposta = await fetch(urlDestino, {
            method: 'POST',
            body: formData
        });

        const dados = await resposta.json();
        if (resposta.ok && dados.sucesso) {
            modal_contato.hide();
            window.location.reload();
        } else {
            console.log(`Erros encontrados no formulário: ${dados.erros}`)
            alert("Não foi possível salvar. Verifique os dados inseridos")
        }
    } catch (erro) {
        console.error("Erro crítico na conexão:", erro)
        alert("Erro ao conectar com o servidor. Tente novamente mais tarde.")
    }
});







