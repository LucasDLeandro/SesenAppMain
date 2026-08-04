let tabelaSolicitacoes;
let tabelaLiberacoes;

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

    $('.select2-empresas').select2({
        theme: 'bootstrap-5',
        dropdownParent: $('#modal-solicitacao')
    });

    tabelaSolicitacoes = $('#tabela-solicitacoes').DataTable({
        responsive: true,
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json"
        },
        ajax: {
            url: '/equipe_tecnica/api/solicitacoes/',
            dataSrc: ''
        },
        columns: [
            { data: 'empresa_nome' },
            { data: 'nome_solicitante' },
            { 
                data: null,
                render: function(data, type, row) {
                    return `${formatDate(row.validade_inicio)} a ${formatDate(row.validade_fim)}`;
                }
            },
            {
                data: 'status',
                render: function(data) {
                    const badges = {
                        'ativa': '<span class="badge bg-success">Ativa</span>',
                        'expirada': '<span class="badge bg-danger">Expirada</span>',
                        'revogada': '<span class="badge bg-secondary">Revogada</span>'
                    };
                    return badges[data] || data;
                }
            },
            {
                data: 'tecnicos_detalhes',
                render: function(data) {
                    return data.map(t => `<span class="badge bg-light text-dark border me-1">${t.nome}</span>`).join('');
                }
            },
            {
                data: null,
                data: null,
                render: function(data, type, row) {
                    return `
                        <div class="d-flex gap-1 flex-nowrap justify-content-end">
                            <button class="btn btn-sm btn-outline-primary" onclick="editarSolicitacao(${row.id})" title="Visualizar/Editar">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-success" onclick="abrirModalLiberacao(${row.id})" title="Gerar Liberação">
                                <i class="bi bi-send-check"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="excluirSolicitacao(${row.id})" title="Excluir">
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

    tabelaLiberacoes = $('#tabela-liberacoes').DataTable({
        responsive: true,
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json"
        },
        ajax: {
            url: '/equipe_tecnica/api/liberacoes/',
            dataSrc: ''
        },
        columns: [
            { data: 'solicitacao' },
            { data: 'empresa_nome' },
            { 
                data: null,
                render: function(data, type, row) {
                    return `${formatDate(row.data_inicio)} a ${formatDate(row.data_fim)}<br><small class="text-muted">${row.periodo}</small>`;
                }
            },
            {
                data: 'tecnicos_detalhes',
                render: function(data) {
                    return data.map(t => `<span class="badge bg-light text-dark border me-1">${t.nome}</span>`).join('');
                }
            },
            {
                data: 'email_enviado',
                render: function(data, type, row) {
                    if(data) return '<span class="badge bg-success">Enviado</span>';
                    if(row.data_agendamento_email) return '<span class="badge bg-warning text-dark">Agendado</span>';
                    return '<span class="badge bg-secondary">Não Enviado</span>';
                }
            },
            {
                data: null,
                render: function(data, type, row) {
                    const previewBtn = `
                        <button class="btn btn-sm btn-outline-info" onclick="visualizarEmailLiberacao(${row.id}, ${!row.email_enviado})" title="${row.email_enviado ? 'Visualizar e-mail enviado' : 'Visualizar e enviar e-mail'}">
                            <i class="bi bi-${row.email_enviado ? 'eye' : 'envelope-open'}"></i>
                        </button>
                    `;
                    return `
                        <div class="d-flex gap-1 flex-nowrap justify-content-end">
                            ${previewBtn}
                            <button class="btn btn-sm btn-outline-danger" onclick="excluirLiberacao(${row.id})" title="Excluir">
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

function formatDate(dateStr) {
    if(!dateStr) return '-';
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
}

let tecnicoCount = 0;
function adicionarLinhaTecnico(tecnico = null) {
    tecnicoCount++;
    const tNome = tecnico ? tecnico.nome : '';
    const tCpf = tecnico ? tecnico.cpf : '';
    const tRg = tecnico ? tecnico.rg : '';
    const tTelefone = tecnico ? tecnico.telefone : '';
    
    // Check global scope (we set IS_ADMIN_OR_SUPERVISOR in the template)
    const isAdmin = typeof IS_ADMIN_OR_SUPERVISOR !== 'undefined' ? IS_ADMIN_OR_SUPERVISOR : true;
    const isEditMode = $('#solicitacao_id').val() !== '';
    const readOnlyAttr = (isEditMode && !isAdmin) ? 'readonly' : '';
    const disabledAttr = (isEditMode && !isAdmin) ? 'disabled' : '';

    const btnRemove = (isEditMode && !isAdmin) ? '' : `
        <button type="button" class="btn btn-sm btn-outline-danger" onclick="$('#tecnico-row-${tecnicoCount}').remove()">
            <i class="bi bi-x"></i>
        </button>`;

    const html = `
        <div class="row g-2 mb-2 align-items-end tecnico-row" id="tecnico-row-${tecnicoCount}">
            <div class="col-md-3">
                <label class="form-label small">Nome</label>
                <input type="text" class="form-control form-control-sm tec-nome format-text" value="${tNome}" required ${readOnlyAttr}>
            </div>
            <div class="col-md-3">
                <label class="form-label small">CPF</label>
                <input type="text" class="form-control form-control-sm tec-cpf mask-cpf" value="${tCpf}" required ${readOnlyAttr}>
            </div>
            <div class="col-md-2">
                <label class="form-label small">RG</label>
                <input type="text" class="form-control form-control-sm tec-rg mask-rg" value="${tRg}" ${readOnlyAttr}>
            </div>
            <div class="col-md-3">
                <label class="form-label small">Telefone</label>
                <input type="text" class="form-control form-control-sm tec-telefone mask-telefone" value="${tTelefone}" ${readOnlyAttr}>
            </div>
            <div class="col-md-1 text-end">
                ${btnRemove}
            </div>
        </div>
    `;
    $('#container-tecnicos').append(html);
}

function abrirModalNovaSolicitacao() {
    $('#form-solicitacao')[0].reset();
    $('#solicitacao_id').val('');
    $('#solicitacao_empresa').val('').trigger('change');
    $('#solicitacao_empresa').prop('disabled', false);
    $('#solicitacao_solicitante').prop('readonly', false);
    $('#solicitacao_data').prop('readonly', false);
    $('#solicitacao_inicio').prop('readonly', false);
    $('#solicitacao_fim').prop('readonly', false);
    $('#btnSalvarSolicitacao').show();
    $('#btnAddTecnico').show();
    
    $('#container-tecnicos').empty();
    adicionarLinhaTecnico(); // adiciona pelo menos 1 linha
    $('#modalSolicitacaoTitle').html('<i class="bi bi-person-badge me-2"></i> Novo Pedido de Acesso');
    $('#modal-solicitacao').modal('show');
}

function editarSolicitacao(id) {
    $.get(`/equipe_tecnica/api/solicitacoes/${id}/`, function(data) {
        $('#solicitacao_id').val(data.id);
        
        // Disable fields if not admin
        const isAdmin = typeof IS_ADMIN_OR_SUPERVISOR !== 'undefined' ? IS_ADMIN_OR_SUPERVISOR : true;
        
        $('#solicitacao_empresa').val(data.empresa).trigger('change');
        $('#solicitacao_solicitante').val(data.nome_solicitante);
        $('#solicitacao_data').val(data.data_solicitacao);
        $('#solicitacao_inicio').val(data.validade_inicio);
        $('#solicitacao_fim').val(data.validade_fim);
        
        if (!isAdmin) {
            $('#solicitacao_empresa').prop('disabled', true);
            $('#solicitacao_solicitante').prop('readonly', true);
            $('#solicitacao_data').prop('readonly', true);
            $('#solicitacao_inicio').prop('readonly', true);
            $('#solicitacao_fim').prop('readonly', true);
            $('#btnSalvarSolicitacao').hide();
            $('#btnAddTecnico').hide();
            $('#modalSolicitacaoTitle').html('<i class="bi bi-eye me-2"></i> Visualizar Pedido de Acesso');
        } else {
            $('#solicitacao_empresa').prop('disabled', false);
            $('#solicitacao_solicitante').prop('readonly', false);
            $('#solicitacao_data').prop('readonly', false);
            $('#solicitacao_inicio').prop('readonly', false);
            $('#solicitacao_fim').prop('readonly', false);
            $('#btnSalvarSolicitacao').show();
            $('#btnAddTecnico').show();
            $('#modalSolicitacaoTitle').html('<i class="bi bi-pencil me-2"></i> Editar Pedido de Acesso');
        }

        $('#container-tecnicos').empty();
        tecnicoCount = 0;
        data.tecnicos_detalhes.forEach(t => {
            adicionarLinhaTecnico(t);
        });

        $('#modal-solicitacao').modal('show');
    });
}

function salvarSolicitacao() {
    const id = $('#solicitacao_id').val();
    
    // Coletar técnicos
    let tecnicos = [];
    $('.tecnico-row').each(function() {
        tecnicos.push({
            nome: $(this).find('.tec-nome').val(),
            cpf: $(this).find('.tec-cpf').val().replace(/\D/g, ''),
            rg: $(this).find('.tec-rg').val().replace(/[\.\-]/g, ''),
            telefone: $(this).find('.tec-telefone').val().replace(/\D/g, '')
        });
    });

    // Need to temporarily enable disabled fields to get their value
    const disabledProps = $('#form-solicitacao').find(':disabled');
    disabledProps.prop('disabled', false);

    const data = {
        empresa: $('#solicitacao_empresa').val(),
        nome_solicitante: $('#solicitacao_solicitante').val(),
        data_solicitacao: $('#solicitacao_data').val(),
        validade_inicio: $('#solicitacao_inicio').val(),
        validade_fim: $('#solicitacao_fim').val(),
        tecnicos_data: tecnicos // enviamos pro backend tratar no create
    };
    
    // Put them back
    disabledProps.prop('disabled', true);

    const url = id ? `/equipe_tecnica/api/solicitacoes/${id}/` : '/equipe_tecnica/api/solicitacoes/';
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
            $('#modal-solicitacao').modal('hide');
            tabelaSolicitacoes.ajax.reload();
            Swal.fire('Sucesso!', 'Solicitação salva com sucesso.', 'success');
        },
        error: function(xhr) {
            Swal.fire('Erro!', 'Verifique os dados e tente novamente.', 'error');
        }
    });
}

function excluirSolicitacao(id) {
    Swal.fire({
        title: 'Tem certeza?',
        text: "Deseja excluir esta solicitação?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/equipe_tecnica/api/solicitacoes/${id}/`,
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function() {
                    Swal.fire('Excluído!', 'Solicitação excluída.', 'success');
                }
            });
        }
    });
}

function abrirModalLiberacao(solicitacao_id) {
    $('#form-liberacao')[0].reset();
    $('#bloco-selecao-pedido').hide();
    $('#lib_select_pedido_geral').removeAttr('required');
    $('#liberacao_solicitacao_id').val(solicitacao_id);
    
    carregarTecnicosDoPedido(solicitacao_id);
    
    $('#modal-liberacao').modal('show');
}

function abrirModalNovaLiberacaoGeral() {
    $('#form-liberacao')[0].reset();
    $('#liberacao_solicitacao_id').val('');
    $('#bloco-selecao-pedido').show();
    $('#lib_select_pedido_geral').attr('required', 'required').html('<option value="">Carregando pedidos ativos...</option>');
    $('#container-tecnicos-liberacao').html('<p class="text-muted mb-0">Selecione um pedido primeiro.</p>');

    $.get('/equipe_tecnica/api/solicitacoes/', function(data) {
        let options = '<option value="">Selecione...</option>';
        data.forEach(s => {
            if(s.status === 'ativa') {
                options += `<option value="${s.id}">${s.empresa_nome} (De ${formatDate(s.validade_inicio)} a ${formatDate(s.validade_fim)})</option>`;
            }
        });
        $('#lib_select_pedido_geral').html(options);
    });

    $('#modal-liberacao').modal('show');
}

function carregarTecnicosDoPedido(solicitacao_id) {
    $('#container-tecnicos-liberacao').empty();
    if(!solicitacao_id) {
        $('#container-tecnicos-liberacao').html('<p class="text-muted mb-0">Selecione um pedido primeiro.</p>');
        return;
    }

    $('#liberacao_solicitacao_id').val(solicitacao_id); // Garante que o ID hidden está atualizado

    $.get(`/equipe_tecnica/api/solicitacoes/${solicitacao_id}/`, function(data) {
        if(data.tecnicos_detalhes.length === 0) {
            $('#container-tecnicos-liberacao').html('<p class="text-danger mb-0">Nenhum técnico cadastrado neste pedido.</p>');
        } else {
            data.tecnicos_detalhes.forEach(t => {
                const checkbox = `
                    <div class="form-check">
                        <input class="form-check-input tec-lib-check" type="checkbox" value="${t.id}" id="tecLib${t.id}">
                        <label class="form-check-label" for="tecLib${t.id}">
                            ${t.nome} (CPF: ${t.cpf})
                        </label>
                    </div>
                `;
                $('#container-tecnicos-liberacao').append(checkbox);
            });
        }
    });
}

function salvarLiberacao() {
    const solicitacao_id = $('#liberacao_solicitacao_id').val();
    
    let tecnicosSelecionados = [];
    $('.tec-lib-check:checked').each(function() {
        tecnicosSelecionados.push($(this).val());
    });

    if(tecnicosSelecionados.length === 0) {
        Swal.fire('Atenção', 'Selecione pelo menos um técnico para liberar o acesso.', 'warning');
        return;
    }

    const data = {
        solicitacao: solicitacao_id,
        tecnicos: tecnicosSelecionados,
        data_inicio: $('#lib_data_inicio').val(),
        data_fim: $('#lib_data_fim').val(),
        periodo: $('#lib_periodo').val(),
    };

    const agendamento = $('#lib_agendamento').val();
    if(agendamento) {
        data.data_agendamento_email = agendamento;
    }

    $.ajax({
        url: '/equipe_tecnica/api/liberacoes/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function() {
            $('#modal-liberacao').modal('hide');
            tabelaLiberacoes.ajax.reload();
            
            if(agendamento) {
                Swal.fire('Agendado!', 'A liberação foi registrada e o e-mail agendado.', 'success');
            } else {
                Swal.fire('Registrado!', 'A liberação foi criada. Você pode enviar o e-mail agora se desejar.', 'success');
            }
        },
        error: function(xhr) {
            Swal.fire('Erro!', 'Ocorreu um erro ao registrar a liberação.', 'error');
        }
    });
}

function excluirLiberacao(id) {
    Swal.fire({
        title: 'Tem certeza?',
        text: "Deseja excluir esta liberação?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/equipe_tecnica/api/liberacoes/${id}/`,
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function() {
                    tabelaLiberacoes.ajax.reload();
                    Swal.fire('Excluído!', 'Liberação excluída.', 'success');
                }
            });
        }
    });
}

let liberacaoEmailPendenteId = null;

function preencherModalPreviewEmail(data, permitirEnvio) {
    $('#preview-template-nome').text(data.template_nome || '-');
    $('#preview-remetente').text(data.remetente || '-');
    $('#preview-destinatario').text(data.destinatario || 'Não configurado');
    $('#preview-assunto').text(data.assunto || '-');
    $('#preview-corpo').text(data.corpo || '');

    if (data.copia_oculta) {
        $('#preview-bcc-row').removeClass('d-none');
        $('#preview-copia').text(data.copia_oculta);
    } else {
        $('#preview-bcc-row').addClass('d-none');
        $('#preview-copia').text('');
    }

    const alerta = $('#preview-email-alerta');
    if (data.erro) {
        alerta.removeClass('d-none alert-success').addClass('alert-warning');
        $('#preview-email-alerta-texto').text(data.erro);
    } else {
        alerta.addClass('d-none');
    }

    if (data.email_enviado) {
        $('#preview-status-badge').replaceWith('<span id="preview-status-badge" class="badge bg-success">Já Enviado</span>');
        $('#preview-info-confirmacao').html('<i class="bi bi-check-circle me-1"></i> Este e-mail já foi enviado.').removeClass('text-muted').addClass('text-success');
    } else {
        $('#preview-status-badge').replaceWith('<span id="preview-status-badge" class="badge bg-secondary">Não Enviado</span>');
        $('#preview-info-confirmacao').html('<i class="bi bi-info-circle me-1"></i> Revise as informações, os anexos e o conteúdo antes de confirmar o envio.').removeClass('text-success').addClass('text-muted');
    }

    if (data.template_nome) {
        $('#preview-template-nome').text(data.template_nome);
    } else {
        $('.email-preview-template-badge').hide();
    }

    $('#preview-destinatario-input').val(data.destinatario || '');
    $('#preview-copia-input').val(data.copia_cc || '');
    $('#preview-assunto-input').val(data.assunto || '');
    
    // Converte br tags para newlines no corpo para o textarea
    let corpoText = data.corpo || '';
    corpoText = corpoText.replace(/<br\s*[\/]?>/gi, "\n");
    $('#preview-corpo-input').val(corpoText);
    
    // Limpa o input de arquivos
    $('#preview-anexos-input').val('');

    if (permitirEnvio && !data.email_enviado) {
        $('#btn-confirmar-envio-email').removeClass('d-none');
    } else {
        $('#btn-confirmar-envio-email').addClass('d-none');
    }
}

function visualizarEmailLiberacao(id, permitirEnvio = false) {
    liberacaoEmailPendenteId = permitirEnvio ? id : null;

    Swal.fire({
        title: 'Carregando pré-visualização...',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });

    $.get(`/equipe_tecnica/api/liberacoes/${id}/preview_email/`, function(data) {
        Swal.close();
        preencherModalPreviewEmail(data, permitirEnvio);
        $('#modal-preview-email').modal('show');
    }).fail(function() {
        Swal.fire('Erro', 'Não foi possível carregar a pré-visualização do e-mail.', 'error');
    });
}

function confirmarEnvioEmail() {
    if (!liberacaoEmailPendenteId) return;

    Swal.fire({
        title: 'Confirmar envio?',
        html: `
            <p class="mb-2">O e-mail será enviado para:</p>
            <p class="fw-bold text-primary mb-0">${$('#preview-destinatario-input').val()}</p>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#16a085',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sim, enviar agora',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (!result.isConfirmed) return;

        const liberacaoId = liberacaoEmailPendenteId;
        $('#modal-preview-email').modal('hide');

        Swal.fire({
            title: 'Enviando...',
            allowOutsideClick: false,
            didOpen: () => { Swal.showLoading(); }
        });

        // Monta o FormData com os campos e anexos
        var formData = new FormData();
        formData.append('to_email', $('#preview-destinatario-input').val());
        formData.append('bcc_email', $('#preview-copia-input').val());
        formData.append('assunto', $('#preview-assunto-input').val());
        formData.append('corpo', $('#preview-corpo-input').val());
        
        var files = $('#preview-anexos-input')[0].files;
        for (var i = 0; i < files.length; i++) {
            formData.append('anexos_externos', files[i]);
        }

        $.ajax({
            url: `/equipe_tecnica/api/liberacoes/${liberacaoId}/enviar_email/`,
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function() {
                liberacaoEmailPendenteId = null;
                Swal.fire('Sucesso!', 'O e-mail de notificação foi enviado com sucesso.', 'success');
                tabelaLiberacoes.ajax.reload(null, false);
            },
            error: function(xhr) {
                let errorMsg = 'Ocorreu um erro ao enviar o e-mail.';
                if (xhr.responseJSON && xhr.responseJSON.status) {
                    errorMsg = xhr.responseJSON.status;
                }
                Swal.fire('Erro', errorMsg, 'error');
            }
        });
    });
}
