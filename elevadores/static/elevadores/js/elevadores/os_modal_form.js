const modal_os_criar = new bootstrap.Modal(document.getElementById('elev-create-os-modal'));
const form_os_criar = document.getElementById('elev-create-os-form');

const modal_os_concluir= new bootstrap.Modal(document.getElementById('elev-concluir-os-modal'));
const form_os_concluir = document.getElementById('elev-concluir-os-form');


//const urlElevCriarOs = form_os_criar.getAttribute('data-url-elev-criar-os');
//const urlElevConcluirOsBase = form_os_concluir.getAttribute('data-url-elev-concluir-os');

const btn_solicitar_elev_os = document.getElementById('elev-btn-solicitar-os')
btn_solicitar_elev_os.addEventListener("click", abrirModalElevSolicitar)

function abrirModalElevSolicitar() {
    form_os_criar.reset();

    id_oculto_elev_os_criar = document.getElementById('id_oculto_elev_os');
    id_oculto_elev_os_criar = "";

    const urlElevRegistrarOsReal = `/elevadores/api/elevadoress/`
    form_os_criar.action = urlElevRegistrarOsReal

    modal_os_criar.show();
}

function abrirModalElevConcluir(id_os, protocolo) {
    document.getElementById('id_oculto_elev_os_concluir').value = id_os
    document.getElementById('id_protocolo_concluir_os').value = protocolo

    //const urlElevConcluirOsReal = urlElevConcluirOsBase.replace('/0/', `/${id_os}/`)
    const urlElevConcluirOsReal = `/elevadores/api/elevadoress/${id_os}/concluir_elev_os/`
    form_os_concluir.action = urlElevConcluirOsReal

    modal_os_concluir.show()
}

const hora_chegada = document.getElementById('id_data_hora_chegada')
const hora_conclusao = document.getElementById('id_data_hora_conclusao')

hora_chegada.addEventListener('change', function() {
    hora_conclusao.value = hora_chegada.value
})

form_os_criar.addEventListener('submit', async function(evento_elev_criar_os) {
    evento_elev_criar_os.preventDefault();

    const urlElevCriarDestino = form_os_criar.action;
    const formDataElevCriar = new FormData(form_os_criar);

    console.log(`urlElevCriarDestino: ${urlElevCriarDestino}`)

    try {
        const resposta = await fetch(urlElevCriarDestino, {
            method:'POST',
            body: formDataElevCriar,
            headers: {
                'X-CSRFToken': formDataElevCriar.get('csrfmiddlewaretoken')
            }
        });

        const dados = await resposta.json();
        if (resposta.ok && dados.sucesso) {
            await Swal.fire({
                title: "Sucesso!",
                text: "A Ordem de Serviço, foi salva com sucesso",
                icon: "success"
            })
            modal_os_criar.hide()
            window.location.reload()
        } else {
            console.log("Erros encontrados no formulário:", dados)
            modal_os_concluir.hide()
            Swal.fire("Erro!", "Não foi possível salvar. Verifique os dados inseridos", "error")
        }

    } catch (erro) {
        console.error("Erro critico na conexão: ", erro)
        alert("Erro ao conectar com o servidor. Tente novamente mais tarde.")
    }
});


form_os_concluir.addEventListener('submit', async function(evento_elev_concluir_os) {
    evento_elev_concluir_os.preventDefault();

    const urlElevConcluirDestino = form_os_concluir.action;
    console.log(urlElevConcluirDestino)
    const formDataElevConcluir = new FormData(form_os_concluir);

    try {
        const resposta = await fetch(urlElevConcluirDestino, {
            method:'POST',
            body: formDataElevConcluir,
            headers: {
                'X-CSRFToken': formDataElevConcluir.get('csrfmiddlewaretoken')
            }
        });

        const dados = await resposta.json();
        if (resposta.ok && dados.sucesso) {
            await Swal.fire({
                title: "Sucesso!",
                text: "A Ordem de Serviço, foi salva com sucesso",
                icon: "success"
            })
            modal_os_concluir.hide()
            window.location.reload()
        } else {
            console.log("Erros encontrados no formulário: ", dados.erros)
            modal_os_concluir.hide()
            Swal.fire("Erro!", "Não foi possível salvar. Verifique os dados inseridos", "error")
        }

    } catch (erro) {
        console.error("Erro critico na conexão: ", erro)
        alert("Erro ao conectar com o servidor. Tente novamente mais tarde.")
    }
});

