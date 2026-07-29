// FORMULÁRIO CONTATO MODAL
// Envolvido em DOMContentLoaded para garantir que os elementos do modal já existam no DOM
document.addEventListener('DOMContentLoaded', function() {
    const form_contato = document.getElementById('contato-form');
    if (!form_contato) return; // Página não possui este modal

    //URLs 
    const urlCriarContato = form_contato.getAttribute('data-url-criar-contato');
    const urlEditarContatoBase = form_contato.getAttribute('data-url-editar-contato');

    // Expor função de update globalmente para ser chamada via onclick nos cards de contato
    window.abrirModalContatoUpdate = function(id, nome, telefone, email, role, notif_elevadores, notif_telefonia, rec_whatsapp, rec_email, status) {
        document.getElementById('id_oculto_contato').value = id;
        document.getElementById('id_nome').value = nome;
        document.getElementById('id_telefone').value = telefone;
        if(document.getElementById('id_email')) document.getElementById('id_email').value = email;
        document.getElementById('id_role').value = role;
        
        // Checkboxes booleanos
        document.getElementById('id_notifica_elevadores').checked = (notif_elevadores === "True");
        document.getElementById('id_notifica_telefonia').checked = (notif_telefonia === "True");
        document.getElementById('id_receber_whatsapp').checked = (rec_whatsapp === "True");
        document.getElementById('id_receber_email').checked = (rec_email === "True");
        document.getElementById('id_contato_is_ativo').checked = (status === "True");

        const urlEditarContatoReal = urlEditarContatoBase.replace('/0/', `/${id}/`);
        form_contato.action = urlEditarContatoReal;

        const modalInst = bootstrap.Modal.getOrCreateInstance(document.getElementById('contatoModal'));
        modalInst.show();
    }

    // Submit do formulário de contato
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
                const inst = bootstrap.Modal.getInstance(document.getElementById('contatoModal'));
                if (inst) inst.hide();
                window.location.reload();
            } else {
                console.log(`Erros encontrados no formulário: ${dados.erros}`)
                Swal.fire("Erro!", "Há um problema com o formulário, verifique os dados.", "error")
            }
        } catch (erro) {
            console.error("Erro crítico na conexão:", erro)
            Swal.fire("Falha!", "Erro ao conectar com o servidor. Tente novamente mais tarde.", "error")
        }
    });

    // Botões de deletar contato
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
                        await Swal.fire({
                            title: "Deletado!",
                            text: "O contato foi deletado!",
                            icon: "success"
                        })
                        window.location.reload();
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

    // Máscara de telefone
    const telInput = document.getElementById('id_telefone');
    if (telInput && typeof IMask !== 'undefined') {
        IMask(telInput, {
            mask: '(00) 0 0000-0000'
        });
    }
});
