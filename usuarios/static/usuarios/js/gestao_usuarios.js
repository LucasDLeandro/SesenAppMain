    let dtUsuarios;

    $(document).ready(function() {
        dtUsuarios = $('#tabela-usuarios').DataTable({
            ajax: {
                url: '/usuarios/api/usuarios/',
                dataSrc: '',
                error: function(xhr, error, code) {
                    console.error("Erro DataTables:", xhr);
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro de Comunicação',
                        text: `Status: ${xhr.status}. Resposta: ${xhr.responseText ? xhr.responseText.substring(0, 100) : 'Sem resposta'}`,
                    });
                }
            },
            columns: [
                { data: 'username' },
                { data: 'first_name', defaultContent: '-' },
                { data: 'last_name', defaultContent: '-' },
                { data: 'email', defaultContent: '-' },
                { data: 'perfil_telefone', defaultContent: '-', className: 'format-telefone' },
                { 
                    data: 'email_boas_vindas_enviado',
                    render: function(data, type, row) {
                        if (data === true) {
                            return '<span class="badge bg-success shadow-sm"><i class="bi bi-check-circle me-1"></i>Enviado</span>';
                        } else {
                            if (row.email_boas_vindas_erro) {
                                // Escapa as aspas e formata para o onClick seguro
                                const erroStr = row.email_boas_vindas_erro.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
                                return `<span class="badge bg-danger shadow-sm" style="cursor:pointer;" onclick="verErroEmail('${erroStr}')" title="Clique para ver o erro"><i class="bi bi-x-circle me-1"></i>Erro no Envio</span>`;
                            } else {
                                return '<span class="badge bg-warning text-dark shadow-sm"><i class="bi bi-clock-history me-1"></i>Pendente</span>';
                            }
                        }
                    }
                },
                {
                    data: 'id',
                    orderable: false,
                    className: 'text-end',
                    render: function(data, type, row) {
                        const safeRow = JSON.stringify(row).replace(/'/g,"&#39;");
                        return `
                            <button class="btn  btn-outline-secondary me-1" onclick="reenviarEmailBoasVindas(${data})" title="Reenviar E-mail (Reseta Senha)">
                                <i class="bi bi-envelope-arrow-up"></i>
                            </button>
                            <button class="btn  btn-outline-primary" onclick='abrirModalEditar(${safeRow})' title="Editar Informações">
                                <i class="bi bi-pencil-square"></i>
                            </button>
                        `;
                    }
                }
            ],
            language: {"sEmptyTable":"Nenhum usuário encontrado","sInfo":"Mostrando de _START_ até _END_ de _TOTAL_ usuários","sInfoEmpty":"Mostrando 0 até 0 de 0 usuários","sInfoFiltered":"(Filtrados de _MAX_ registros)","sLengthMenu":"Mostrar _MENU_ resultados por página","sLoadingRecords":"Carregando...","sProcessing":"Processando...","sZeroRecords":"Nenhum usuário encontrado","sSearch":"Pesquisar:","oPaginate": {"sNext":"Próximo","sPrevious":"Anterior","sFirst":"Primeiro","sLast":"Último"
                }
            }
        });
    });

    function abrirModalCriar() {
        document.getElementById('form-criar-usuario').reset();
        // Reset defaults
        document.querySelector('#form-criar-usuario [name="is_active"]').checked = true;
        document.querySelector('#form-criar-usuario [name="password"]').value = window.DEFAULT_PASSWORD;
        document.querySelector('#form-criar-usuario [name="telefone"]').value = '61';
        new bootstrap.Modal(document.getElementById('modal-criar-usuario')).show();
    }

    async function salvarNovoUsuario(e) {
        e.preventDefault();
        const form = e.target;
        const payload = {
            username: form.username.value,
            password: form.password.value,
            first_name: form.first_name.value,
            last_name: form.last_name.value,
            email: form.email.value,
            telefone: form.telefone.value
        };

        try {
            const res = await fetch('/usuarios/api/usuarios/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const data = await res.json();
                bootstrap.Modal.getInstance(document.getElementById('modal-criar-usuario')).hide();
                dtUsuarios.ajax.reload();
                
                if (data.email_boas_vindas_enviado) {
                    Swal.fire('Criado!', 'Usuário criado e e-mail de boas-vindas enviado com sucesso.', 'success');
                } else if (data.email_boas_vindas_erro) {
                    Swal.fire('Criado com Alerta!', 'Usuário criado, mas houve erro ao enviar o e-mail:<br><br><span class="text-danger" >' + data.email_boas_vindas_erro + '</span>', 'warning');
                } else {
                    Swal.fire('Criado!', 'Usuário criado com sucesso (envio de e-mail desativado).', 'success');
                }
            } else {
                const error = await res.json();
                Swal.fire('Erro!', JSON.stringify(error), 'error');
            }
        } catch(err) {
            Swal.fire('Erro!', 'Erro de conexão.', 'error');
        }
    }

    function abrirModalEditar(row) {
        document.getElementById('edit_user_id').value = row.id;
        document.getElementById('edit_username').value = row.username;
        document.getElementById('edit_password').value = '';
        document.getElementById('edit_first_name').value = row.first_name || '';
        document.getElementById('edit_last_name').value = row.last_name || '';
        document.getElementById('edit_email').value = row.email || '';
        document.getElementById('edit_telefone').value = row.perfil_telefone || '';

        new bootstrap.Modal(document.getElementById('modal-editar-usuario')).show();
    }

    async function salvarEdicaoUsuario(e) {
        e.preventDefault();
        const id = document.getElementById('edit_user_id').value;
        const payload = {
            first_name: document.getElementById('edit_first_name').value,
            last_name: document.getElementById('edit_last_name').value,
            email: document.getElementById('edit_email').value,
            telefone: document.getElementById('edit_telefone').value
        };

        const pwd = document.getElementById('edit_password').value;
        if(pwd) payload.password = pwd;

        try {
            const res = await fetch(`/usuarios/api/usuarios/${id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                bootstrap.Modal.getInstance(document.getElementById('modal-editar-usuario')).hide();
                dtUsuarios.ajax.reload();
                Swal.fire('Atualizado!', 'Usuário atualizado com sucesso.', 'success');
            } else {
                const error = await res.json();
                Swal.fire('Erro!', JSON.stringify(error), 'error');
            }
        } catch(err) {
            Swal.fire('Erro!', 'Erro de conexão.', 'error');
        }
    }

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

    function verErroEmail(erro) {
        document.getElementById('erro-email-conteudo').innerText = erro;
        new bootstrap.Modal(document.getElementById('modalErroEmail')).show();
    }

    async function reenviarEmailBoasVindas(userId) {
        if (!confirm(`Deseja reenviar o e-mail de boas-vindas? Isso irá redefinir a senha do usuário para"${window.DEFAULT_PASSWORD}" e tentará disparar o e-mail novamente.`)) return;

        Swal.fire({
            title: 'Enviando...',
            text: 'Aguarde enquanto tentamos comunicar com o servidor de e-mail.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        try {
            const res = await fetch(`/usuarios/api/usuarios/${userId}/reenviar_email_boas_vindas/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            const data = await res.json();
            if (res.ok) {
                Swal.fire('Sucesso!', 'E-mail reenviado com sucesso.', 'success');
                dtUsuarios.ajax.reload(null, false);
            } else {
                const erroMsg = data.error ? `Detalhe do Servidor: ${data.error}` : (data.detail || 'Falha ao reenviar e-mail.');
                Swal.fire('Erro no Envio!', erroMsg, 'error');
                dtUsuarios.ajax.reload(null, false);
            }
        } catch (e) {
            Swal.fire('Erro!', 'Erro de conexão com a API.', 'error');
            console.error(e);
        }
    }

    // Inicialização do Select2 para Busca Global de Contatos no Modal de Criação
    $(document).ready(function() {
        $('#global-contact-import').select2({
            theme: 'bootstrap-5',
            dropdownParent: $('#modal-criar-usuario'),
            placeholder: '🔍 Importar dados de um Contato da Base Global...',
            allowClear: true,
            ajax: {
                url: '/usuarios/api/global-contacts/search/',
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return { q: params.term };
                },
                processResults: function (data) {
                    return { results: data.results };
                },
                cache: true
            }
        }).on('select2:select', function (e) {
            var data = e.params.data;
            
            // Tenta adivinhar nome e sobrenome
            let names = data.nome.split(' ');
            let firstName = names[0];
            let lastName = names.slice(1).join(' ');
            
            document.getElementById('create_first_name').value = firstName || '';
            document.getElementById('create_last_name').value = lastName || '';
            document.getElementById('create_email').value = data.email || '';
            document.getElementById('create_telefone').value = data.telefone || '';
            
            // Sugere um username baseado no email ou nome
            if (data.email) {
                document.getElementById('create_username').value = data.email.split('@')[0];
            } else {
                document.getElementById('create_username').value = firstName.toLowerCase() + (lastName ? '.' + names[names.length-1].toLowerCase() : '');
            }
            
            $(this).val(null).trigger('change'); // Limpa a busca após importação
        });
    });
