let tabelaEmpresas;

$(document).ready(function() {
    // Função utilitária para aplicar filtros de pesquisa individual por coluna
    function aplicarFiltroColunas(tabela) {
        var tableNode = tabela.table().node();
        var thead = $(tableNode).find('thead');
        
        // Verifica se a linha de filtros já existe para evitar duplicidade
        if (thead.find('.filter-row').length) return;

        var tr = $('<tr class="filter-row"></tr>');

        tabela.columns().every(function(index) {
            var column = this;
            var headerText = $(column.header()).text().trim();
            var th = $('<th></th>');

            if (headerText.toLowerCase() === 'ações' || headerText.toLowerCase() === 'acões' || headerText === '') {
                th.appendTo(tr);
                return;
            }

            var input = $('<input type="text" class="form-control form-control-sm" />')
                .attr('placeholder', 'Filtrar ' + headerText)
                .css({
                    'width': '100%',
                    'font-size': '12px',
                    'padding': '4px 8px',
                    'border': '1px solid #ced4da',
                    'border-radius': '4px',
                    'background-color': '#f8f9fa'
                });

            var debounceTimer;
            input.on('keyup change', function() {
                var self = this;
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(function() {
                    if (column.search() !== self.value) {
                        column.search(self.value).draw();
                    }
                }, 300);
            });

            input.on('click', function(e) { e.stopPropagation(); });

            th.append(input).appendTo(tr);
        });

        thead.append(tr);
    }

    tabelaEmpresas = $('#tabela-empresas').DataTable({
        responsive: true,
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json"
        },
        ajax: {
            url: '/empresas/api/empresas/',
            dataSrc: ''
        },
        columns: [
            { data: 'nome_empresa' },
            { data: 'cnpj' },
            { 
                data: 'classificacao',
                render: function(data) {
                    if (data) {
                        return `<span class="badge bg-secondary">${data}</span>`;
                    }
                    return '-';
                }
            },
            { 
                data: null,
                render: function(data, type, row) {
                    return `${row.cidade || '-'} / ${row.estado || '-'}`;
                }
            },
            {
                data: 'contatos',
                render: function(data) {
                    const count = data ? data.length : 0;
                    if (count > 0) {
                        return `<span class="badge bg-primary rounded-pill">${count}</span>`;
                    }
                    return `<span class="badge bg-light text-muted rounded-pill">0</span>`;
                }
            },
            {
                data: null,
                render: function(data, type, row) {
                    return `
                        <div class="d-flex gap-1 flex-nowrap justify-content-end">
                            <button class="btn btn-sm btn-outline-info" onclick="abrirModalContatos(${row.id})" title="Contatos">
                                <i class="bi bi-people"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-primary" onclick="editarEmpresa(${row.id})" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="excluirEmpresa(${row.id})" title="Excluir">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    `;
                },
                className: 'text-end'
            }
        ],
        orderCellsTop: true,
        initComplete: function() {
            aplicarFiltroColunas(this.api());
        }
    });
});

// ==================== EMPRESAS ====================

function abrirModalNovaEmpresa() {
    $('#form-empresa')[0].reset();
    $('#empresa_id').val('');
    $('#empresa_classificacao').val('');
    $('#empresa_cargo').val('');
    $('#empresaModalTitle').text('Nova Empresa');
    $('#modal-empresa').modal('show');
}

function editarEmpresa(id) {
    $.get(`/empresas/api/empresas/${id}/`, function(data) {
        $('#empresa_id').val(data.id);
        $('#empresa_nome').val(data.nome_empresa);
        const cnpjEl = $('#empresa_cnpj').val(data.cnpj)[0];
        if (cnpjEl) cnpjEl.dispatchEvent(new Event('input', {bubbles: true}));
        $('#empresa_classificacao').val(data.classificacao || '');
        $('#empresa_cargo').val(data.cargo || '');
        const cepEl = $('#empresa_cep').val(data.cep)[0];
        if (cepEl) cepEl.dispatchEvent(new Event('input', {bubbles: true}));
        $('#empresa_rua').val(data.rua);
        $('#empresa_numero').val(data.numero);
        $('#empresa_bairro').val(data.bairro);
        $('#empresa_cidade').val(data.cidade);
        $('#empresa_estado').val(data.estado);
        $('#empresaModalTitle').text('Editar Empresa');
        $('#modal-empresa').modal('show');
    });
}

function salvarEmpresa() {
    const form = document.getElementById('form-empresa');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const id = $('#empresa_id').val();
    const data = {
        nome_empresa: $('#empresa_nome').val(),
        cnpj: $('#empresa_cnpj').val().replace(/\D/g, ''),
        classificacao: $('#empresa_classificacao').val(),
        cargo: $('#empresa_cargo').val(),
        cep: $('#empresa_cep').val().replace(/\D/g, ''),
        rua: $('#empresa_rua').val(),
        numero: $('#empresa_numero').val(),
        bairro: $('#empresa_bairro').val(),
        cidade: $('#empresa_cidade').val(),
        estado: $('#empresa_estado').val(),
    };

    const url = id ? `/empresas/api/empresas/${id}/` : '/empresas/api/empresas/';
    const method = id ? 'PUT' : 'POST';

    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(data),
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function() {
            $('#modal-empresa').modal('hide');
            tabelaEmpresas.ajax.reload();
            Swal.fire('Sucesso!', 'Empresa salva com sucesso.', 'success');
        },
        error: function(xhr) {
            let msg = 'Ocorreu um erro ao salvar a empresa.';
            if (xhr.responseJSON) {
                const erros = Object.values(xhr.responseJSON).flat();
                if (erros.length) msg = erros.join('<br>');
            }
            Swal.fire('Erro!', msg, 'error');
        }
    });
}

function excluirEmpresa(id) {
    Swal.fire({
        title: 'Tem certeza?',
        text: "Deseja realmente excluir esta empresa? Todos os contatos vinculados serão removidos.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/empresas/api/empresas/${id}/`,
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function() {
                    tabelaEmpresas.ajax.reload();
                    Swal.fire('Excluído!', 'A empresa foi excluída.', 'success');
                }
            });
        }
    });
}

// ==================== CONTATOS ====================

function abrirModalContatos(empresaId) {
    $('#contatos_empresa_id').val(empresaId);
    $('#form-novo-contato')[0].reset();
    
    // Buscar dados da empresa para exibir o nome
    $.get(`/empresas/api/empresas/${empresaId}/`, function(data) {
        $('#contatosEmpresaNome').text(data.nome_empresa);
        renderizarContatos(data.contatos || []);
        $('#modal-contatos').modal('show');
    });
}

function renderizarContatos(contatos) {
    const container = $('#lista-contatos');
    container.empty();
    
    if (!contatos || contatos.length === 0) {
        container.html(`
            <div class="text-center text-muted py-3" id="sem-contatos">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                Nenhum contato registrado para esta empresa.
            </div>
        `);
        return;
    }

    contatos.forEach(function(contato) {
        const card = `
            <div class="contato-card d-flex justify-content-between align-items-start" id="contato-${contato.id}">
                <div class="flex-grow-1">
                    <div class="fw-bold text-dark"><i class="bi bi-person me-1"></i>${contato.nome_contato} ${contato.sobrenome || ''}</div>
                    ${contato.cargo ? `<div class="small text-primary"><i class="bi bi-briefcase me-1"></i>${contato.cargo}</div>` : ''}
                    <div class="small text-muted mt-1">
                        ${contato.email ? `<span class="me-3"><i class="bi bi-envelope me-1"></i>${contato.email}</span>` : ''}
                        ${contato.telefone ? `<span><i class="bi bi-telephone me-1"></i>${contato.telefone}</span>` : ''}
                    </div>
                </div>
                <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-outline-primary btn-remove-contato" onclick="editarContato(${contato.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger btn-remove-contato" onclick="excluirContato(${contato.id})" title="Excluir">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
            </div>
        `;
        container.append(card);
    });
}

function adicionarContato() {
    const empresaId = $('#contatos_empresa_id').val();
    const nome = $('#contato_nome').val().trim();
    
    if (!nome) {
        Swal.fire('Atenção', 'Informe o nome do contato.', 'warning');
        return;
    }

    const data = {
        empresa: empresaId,
        nome_contato: nome,
        sobrenome: $('#contato_sobrenome').val().trim(),
        cargo: $('#contato_cargo').val().trim(),
        email: $('#contato_email').val().trim(),
        telefone: $('#contato_telefone').val().replace(/\D/g, ''),
    };

    const url = '/empresas/api/contatos/';
    const method = 'POST';

    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(data),
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function() {
            $('#form-novo-contato')[0].reset();
            recarregarContatos(empresaId);
            tabelaEmpresas.ajax.reload(null, false);
            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: 'success',
                title: 'Contato adicionado!',
                showConfirmButton: false,
                timer: 2000
            });
        },
        error: function(xhr) {
            let msg = 'Erro ao salvar contato.';
            if (xhr.responseJSON) {
                const erros = Object.values(xhr.responseJSON).flat();
                if (erros.length) msg = erros.join('<br>');
            }
            Swal.fire('Erro!', msg, 'error');
        }
    });
}

function editarContato(contatoId) {
    $.get(`/empresas/api/contatos/${contatoId}/`, function(data) {
        $('#edit_contato_id').val(data.id);
        $('#edit_contato_nome').val(data.nome_contato || '');
        $('#edit_contato_sobrenome').val(data.sobrenome || '');
        $('#edit_contato_email').val(data.email || '');
        const telEl = $('#edit_contato_telefone').val(data.telefone || '')[0];
        if (telEl) telEl.dispatchEvent(new Event('input', {bubbles: true}));
        $('#edit_contato_cargo').val(data.cargo || '');
        
        $('#modal-editar-contato').modal('show');
    });
}

function salvarEdicaoContato() {
    const empresaId = $('#contatos_empresa_id').val();
    const contatoEditId = $('#edit_contato_id').val();
    const nome = $('#edit_contato_nome').val().trim();
    
    if (!nome) {
        Swal.fire('Atenção', 'Informe o nome do contato.', 'warning');
        return;
    }

    const data = {
        empresa: empresaId,
        nome_contato: nome,
        sobrenome: $('#edit_contato_sobrenome').val().trim(),
        cargo: $('#edit_contato_cargo').val().trim(),
        email: $('#edit_contato_email').val().trim(),
        telefone: $('#edit_contato_telefone').val().replace(/\D/g, ''),
    };

    $.ajax({
        url: `/empresas/api/contatos/${contatoEditId}/`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data),
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function() {
            $('#modal-editar-contato').modal('hide');
            recarregarContatos(empresaId);
            tabelaEmpresas.ajax.reload(null, false);
            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: 'success',
                title: 'Contato atualizado!',
                showConfirmButton: false,
                timer: 2000
            });
        },
        error: function(xhr) {
            let msg = 'Erro ao atualizar contato.';
            if (xhr.responseJSON) {
                const erros = Object.values(xhr.responseJSON).flat();
                if (erros.length) msg = erros.join('<br>');
            }
            Swal.fire('Erro!', msg, 'error');
        }
    });
}

function excluirContato(contatoId) {
    const empresaId = $('#contatos_empresa_id').val();
    
    Swal.fire({
        title: 'Excluir contato?',
        text: "Esta ação não pode ser desfeita.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/empresas/api/contatos/${contatoId}/`,
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function() {
                    recarregarContatos(empresaId);
                    tabelaEmpresas.ajax.reload(null, false);
                    Swal.fire({
                        toast: true,
                        position: 'top-end',
                        icon: 'success',
                        title: 'Contato removido!',
                        showConfirmButton: false,
                        timer: 2000
                    });
                }
            });
        }
    });
}

function recarregarContatos(empresaId) {
    $.get(`/empresas/api/empresas/${empresaId}/`, function(data) {
        renderizarContatos(data.contatos || []);
    });
}
