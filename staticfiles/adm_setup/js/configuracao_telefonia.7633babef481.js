window.abrirModalConfig = function() {
    fetch('/reembolsos/api/configuracao-pdf/')
        .then(response => {
            if(!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            document.getElementById('config-cabecalho_linha1').value = data.cabecalho_linha1;
            document.getElementById('config-cabecalho_linha2').value = data.cabecalho_linha2;
            document.getElementById('config-cabecalho_linha3').value = data.cabecalho_linha3;
            document.getElementById('config-titulo_tabela_anual').value = data.titulo_tabela_anual;
            document.getElementById('config-nota_rodape_1').value = data.nota_rodape_1;
            document.getElementById('config-nota_rodape_2_prefix').value = data.nota_rodape_2_prefix;
            
            var modal = new bootstrap.Modal(document.getElementById('modalConfig'));
            modal.show();
        })
        .catch(err => {
            Swal.fire('Erro', 'Não foi possível carregar as configurações', 'error');
        });
}

window.salvarConfig = function() {
    // Pegar o CSRF token do template ou do cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const data = {
        cabecalho_linha1: document.getElementById('config-cabecalho_linha1').value,
        cabecalho_linha2: document.getElementById('config-cabecalho_linha2').value,
        cabecalho_linha3: document.getElementById('config-cabecalho_linha3').value,
        titulo_tabela_anual: document.getElementById('config-titulo_tabela_anual').value,
        nota_rodape_1: document.getElementById('config-nota_rodape_1').value,
        nota_rodape_2_prefix: document.getElementById('config-nota_rodape_2_prefix').value
    };

    fetch('/reembolsos/api/configuracao-pdf/', {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if(!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        var modalInstance = bootstrap.Modal.getInstance(document.getElementById('modalConfig'));
        if (modalInstance) modalInstance.hide();
        Swal.fire({
            icon: 'success',
            title: 'Salvo!',
            text: 'Configurações de PDF atualizadas com sucesso.',
            timer: 2000,
            showConfirmButton: false
        }).then(() => {
            window.location.reload();
        });
    })
    .catch(err => {
        Swal.fire('Erro', 'Não foi possível salvar as configurações', 'error');
    });
}

window.editarTemplateWhatsapp = function(id, mensagem) {
    document.getElementById('whatsapp_template_id').value = id;
    document.getElementById('whatsapp_mensagem').value = mensagem;
    
    var modal = new bootstrap.Modal(document.getElementById('modalTemplateWhatsapp'));
    modal.show();
}
