async function salvarMeuPerfilModal(e) {
    e.preventDefault();
    const id = document.getElementById('modal_perfil_user_id').value;
    const payload = {
        first_name: document.getElementById('modal_perfil_first_name').value,
        last_name: document.getElementById('modal_perfil_last_name').value,
        email: document.getElementById('modal_perfil_email').value,
        telefone: document.getElementById('modal_perfil_telefone').value
    };

    try {
        Swal.fire({
            title: 'Salvando...',
            allowOutsideClick: false,
            didOpen: () => { Swal.showLoading(); }
        });

        const res = await fetch(`/usuarios/api/usuarios/${id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookieModal('csrftoken')
            },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            Swal.fire('Atualizado!', 'Seu perfil foi atualizado com sucesso.', 'success').then(() => {
                const modalEl = document.getElementById('modal-perfil-usuario');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if(modal) modal.hide();
                location.reload();
            });
        } else {
            const error = await res.json();
            Swal.fire('Erro!', JSON.stringify(error), 'error');
        }
    } catch(err) {
        Swal.fire('Erro!', 'Erro de conexão.', 'error');
    }
}

function getCookieModal(name) {
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
