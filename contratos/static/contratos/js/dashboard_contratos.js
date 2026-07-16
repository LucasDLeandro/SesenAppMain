let tabelaContratos;

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
        dropdownParent: $('#modal-contrato')
    });

    tabelaContratos = $('#tabela-contratos').DataTable({
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json"
        },
        ajax: {
            url: '/contratos/api/contratos/',
            dataSrc: ''
        },
        columns: [
            { data: 'num_contrato' },
            { 
                data: null,
                render: function(data, type, row) {
                    return `<strong>${row.empresa_nome}</strong><br><small class="text-muted">${row.empresa_cnpj}</small>`;
                }
            },
            { 
                data: null,
                render: function(data, type, row) {
                    return `${formatDate(row.inicio_vigencia)} a ${formatDate(row.termino_vigencia)}`;
                }
            },
            {
                data: 'valor',
                render: function(data) {
                    return parseFloat(data).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                }
            },
            {
                data: 'status',
                render: function(data) {
                    const badges = {
                        'VIGENTE': '<span class="badge bg-success">Vigente</span>',
                        'ENCERRADO': '<span class="badge bg-danger">Encerrado</span>',
                        'SUSPENSO': '<span class="badge bg-warning text-dark">Suspenso</span>'
                    };
                    return badges[data] || `<span class="badge bg-secondary">${data}</span>`;
                }
            },
            {
                data: null,
                render: function(data, type, row) {
                    return `
                        <div class="d-flex gap-1 flex-nowrap justify-content-end">
                            <button class="btn btn-sm btn-outline-primary" onclick="editarContrato(${row.id})" title="Editar">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="excluirContrato(${row.id})" title="Excluir">
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

    // Chama a função para carregar os cartões
    carregarContratacoesCards();

    let tabelaTramitacoes = $('#tabela-tramitacoes').DataTable({
        language: { url: "https://cdn.datatables.net/plug-ins/1.13.4/i18n/pt-BR.json" },
        ajax: { url: '/contratos/api/tramitacoes/', dataSrc: '' },
        columns: [
            { 
                data: 'contratacao',
                render: function(data, type, row) { return row.contratacao_numero || data; } // Will need expand from backend or just show ID for now
            },
            { data: 'unidade_atual' },
            { data: 'data_entrada', render: function(data) { return formatDate(data); } },
            { data: 'tempo_na_unidade' },
            { 
                data: 'dentro_do_cronograma',
                render: function(data) {
                    return data ? '<span class="badge bg-success">No Prazo</span>' : '<span class="badge bg-danger">Atrasado</span>';
                }
            },
            { data: 'atualizado_por_nome' }
        ],
        orderCellsTop: true,
        initComplete: function() {
            aplicarFiltroColunas(this.api());
        }
    });

    // Reajustar colunas do DataTable ao trocar de aba
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        $.fn.dataTable.tables({ visible: true, api: true }).columns.adjust();
    });

    // Inicializar IMask para valor previsto
    const valorPrevistoEl = document.getElementById('valor_previsto');
    if (valorPrevistoEl) {
        window.valorPrevistoMask = IMask(valorPrevistoEl, {
            mask: Number,
            scale: 2,
            signed: false,
            thousandsSeparator: '.',
            padFractionalZeros: true,
            normalizeZeros: true,
            radix: ',',
            mapToRadix: ['.']
        });
    }
});

function formatDate(dateStr) {
    if(!dateStr) return '-';
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
}

function abrirModalNovoContrato() {
    $('#form-contrato')[0].reset();
    $('#contrato_id').val('');
    $('#contrato_empresa').val('').trigger('change');
    $('#processo_licitatorio').val('');
    $('#valor_mensal_estimado').val('');
    $('#gestor_titular').val('');
    $('#gestor_substituto').val('');
    $('#fiscal_titular').val('');
    $('#fiscal_substituto').val('');
    $('#modalContratoTitle').html('<i class="bi bi-file-earmark-plus me-2 text-primary"></i>Novo Contrato');
    $('#modal-contrato').modal('show');
}

function editarContrato(id) {
    $.get(`/contratos/api/contratos/${id}/`, function(data) {
        $('#contrato_id').val(data.id);
        $('#contrato_empresa').val(data.empresa).trigger('change');
        $('#processo_licitatorio').val(data.processo_licitatorio || '');
        $('#num_contrato').val(data.num_contrato);
        $('#inicio_vigencia').val(data.inicio_vigencia);
        $('#termino_vigencia').val(data.termino_vigencia);
        $('#objeto').val(data.objeto);
        $('#valor').val(data.valor);
        $('#valor_mensal_estimado').val(data.valor_mensal_estimado);
        
        $('#gestor_titular').val(data.gestor_titular || '');
        $('#gestor_substituto').val(data.gestor_substituto || '');
        $('#fiscal_titular').val(data.fiscal_titular || '');
        $('#fiscal_substituto').val(data.fiscal_substituto || '');
        
        $('#sei_processo').val(data.sei_processo);
        $('#sei_dod').val(data.sei_dod);
        $('#sei_etp').val(data.sei_etp);
        $('#sei_tr').val(data.sei_tr);
        $('#sei_edital').val(data.sei_edital);
        $('#sei_fiscais').val(data.sei_fiscais);
        $('#status').val(data.status);
        
        $('#modalContratoTitle').html('<i class="bi bi-pencil me-2 text-primary"></i>Editar Contrato');
        $('#modal-contrato').modal('show');
    });
}

function salvarContrato() {
    // Revalidar form
    const form = document.getElementById('form-contrato');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const id = $('#contrato_id').val();
    
    const data = {
        empresa: $('#contrato_empresa').val(),
        processo_licitatorio: $('#processo_licitatorio').val() || null,
        num_contrato: $('#num_contrato').val(),
        inicio_vigencia: $('#inicio_vigencia').val(),
        termino_vigencia: $('#termino_vigencia').val(),
        objeto: $('#objeto').val(),
        valor: $('#valor').val(),
        valor_mensal_estimado: $('#valor_mensal_estimado').val() || 0,
        gestor_titular: $('#gestor_titular').val(),
        gestor_substituto: $('#gestor_substituto').val(),
        fiscal_titular: $('#fiscal_titular').val(),
        fiscal_substituto: $('#fiscal_substituto').val(),
        sei_processo: $('#sei_processo').val(),
        sei_dod: $('#sei_dod').val(),
        sei_etp: $('#sei_etp').val(),
        sei_tr: $('#sei_tr').val(),
        sei_edital: $('#sei_edital').val(),
        sei_fiscais: $('#sei_fiscais').val(),
        status: $('#status').val(),
    };
    
    const url = id ? `/contratos/api/contratos/${id}/` : '/contratos/api/contratos/';
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
            $('#modal-contrato').modal('hide');
            tabelaContratos.ajax.reload();
            Swal.fire('Sucesso!', 'Contrato salvo com sucesso.', 'success');
        },
        error: function(xhr) {
            console.error(xhr.responseText);
            Swal.fire('Erro!', 'Não foi possível salvar o contrato. Verifique os dados.', 'error');
        }
    });
}

function excluirContrato(id) {
    Swal.fire({
        title: 'Tem certeza?',
        text: "Deseja excluir este contrato?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/contratos/api/contratos/${id}/`,
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function() {
                    tabelaContratos.ajax.reload();
                    Swal.fire('Excluído!', 'Contrato excluído.', 'success');
                }
            });
        }
    });
}

function abrirModalNovaContratacao() {
    $('#form-contratacao')[0].reset();
    $('#contratacao_id').val('');
    if (window.valorPrevistoMask) {
        window.valorPrevistoMask.value = '0,00';
    }
    $('#modalContratacaoTitle').html('<i class="bi bi-diagram-3 me-2 text-info"></i>Nova Contratação');
    $('#modal-contratacao').modal('show');
}

function editarContratacao(id) {
    $.get(`/contratos/api/processos/${id}/`, function(data) {
        $('#contratacao_id').val(data.id);
        $('#numero_processo').val(data.numero_processo);
        $('#unidade_responsavel').val(data.unidade_responsavel);
        $('#servidor_responsavel').val(data.servidor_responsavel);
        $('#fase').val(data.fase);
        $('#objeto_lic').val(data.objeto);
        $('#descricao_objeto').val(data.descricao_objeto);
        $('#justificativa').val(data.justificativa);
        
        if (window.valorPrevistoMask) {
            window.valorPrevistoMask.unmaskedValue = (data.valor_previsto || 0).toString();
        } else {
            $('#valor_previsto').val(data.valor_previsto || 0);
        }
        
        $('#prioridade').val(data.prioridade || 'MEDIA');
        $('#data_prevista_conclusao').val(data.data_prevista_conclusao);
        $('#esta_no_pac').prop('checked', data.esta_no_pac);
        $('#eleicoes_ano_corrente').prop('checked', data.eleicoes_ano_corrente);
        $('#observacoes').val(data.observacoes);
        
        $('#modalContratacaoTitle').html('<i class="bi bi-pencil me-2 text-info"></i>Editar Contratação');
        $('#modal-contratacao').modal('show');
    });
}

function salvarContratacao() {
    const form = document.getElementById('form-contratacao');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const id = $('#contratacao_id').val();
    
    // Obter o valor numérico limpo (unmasked)
    let valor_previsto_num = 0;
    if (window.valorPrevistoMask) {
        valor_previsto_num = window.valorPrevistoMask.unmaskedValue;
    } else {
        // Fallback caso a máscara não tenha sido inicializada
        const valStr = $('#valor_previsto').val().replace(/\./g, '').replace(',', '.');
        valor_previsto_num = parseFloat(valStr);
    }
    
    const data = {
        numero_processo: $('#numero_processo').val(),
        unidade_responsavel: $('#unidade_responsavel').val(),
        servidor_responsavel: $('#servidor_responsavel').val(),
        fase: $('#fase').val(),
        objeto: $('#objeto_lic').val(),
        descricao_objeto: $('#descricao_objeto').val(),
        justificativa: $('#justificativa').val(),
        valor_previsto: valor_previsto_num || 0,
        prioridade: $('#prioridade').val(),
        data_prevista_conclusao: $('#data_prevista_conclusao').val() || null,
        esta_no_pac: $('#esta_no_pac').is(':checked'),
        eleicoes_ano_corrente: $('#eleicoes_ano_corrente').is(':checked'),
        observacoes: $('#observacoes').val()
    };

    const url = id ? `/contratos/api/processos/${id}/` : '/contratos/api/processos/';
    const method = id ? 'PUT' : 'POST';

    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(data),
        headers: { 'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val() },
        success: function() {
            $('#modal-contratacao').modal('hide');
            carregarContratacoesCards();
            Swal.fire('Sucesso!', 'Contratação salva.', 'success');
        },
        error: function(xhr) {
            console.error(xhr.responseText);
            Swal.fire('Erro!', 'Não foi possível salvar.', 'error');
        }
    });
}

function abrirModalNovaTramitacao() {
    $('#form-tramitacao')[0].reset();
    $('#tramitacao_id').val('');
    // Set current date
    const today = new Date();
    document.getElementById('data_entrada').valueAsDate = today;
    document.getElementById('data_ultima_movimentacao').valueAsDate = today;
    $('#modalTramitacaoTitle').html('<i class="bi bi-clock-history me-2 text-warning"></i>Lançar Tramitação SEI');
    $('#modal-tramitacao').modal('show');
}

function editarTramitacao(tramitacaoId, processoId) {
    if (!window.processosGlobais) return;
    const proc = window.processosGlobais.find(p => p.id === processoId);
    if (!proc) return;
    const t = proc.tramitacoes.find(x => x.id === tramitacaoId);
    if (!t) return;
    
    $('#form-tramitacao')[0].reset();
    $('#tramitacao_id').val(t.id);
    $('#tramitacao_contratacao').val(proc.id);
    
    if (t.data_entrada) document.getElementById('data_entrada').value = t.data_entrada.substring(0, 10);
    if (t.data_ultima_movimentacao) document.getElementById('data_ultima_movimentacao').value = t.data_ultima_movimentacao.substring(0, 10);
    
    $('#unidade_atual').val(t.unidade_atual || '');
    $('#unidade_ultima_assinatura').val(t.unidade_ultima_assinatura || '');
    $('#atribuido_a').val(t.atribuido_a || '');
    $('#motivo').val(t.motivo || '');
    $('#depende_de_nos').prop('checked', t.depende_de_nos || false);
    
    if (t.prazo_retorno) document.getElementById('prazo_retorno').value = t.prazo_retorno.substring(0, 10);
    
    $('#modalTramitacaoTitle').html('<i class="bi bi-pencil-square me-2 text-warning"></i>Editar Tramitação SEI');
    
    // Hide details modal if open
    const modalDetalhes = bootstrap.Modal.getInstance(document.getElementById('modalDetalhesProcesso'));
    if (modalDetalhes) modalDetalhes.hide();
    
    $('#modal-tramitacao').modal('show');
}

function salvarTramitacao() {
    const form = document.getElementById('form-tramitacao');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const id = $('#tramitacao_id').val();
    const data = {
        contratacao: $('#tramitacao_contratacao').val(),
        data_entrada: $('#data_entrada').val(), 
        data_ultima_movimentacao: $('#data_ultima_movimentacao').val() || null,
        unidade_atual: $('#unidade_atual').val(),
        unidade_ultima_assinatura: $('#unidade_ultima_assinatura').val(),
        atribuido_a: $('#atribuido_a').val(),
        motivo: $('#motivo').val(),
        depende_de_nos: $('#depende_de_nos').is(':checked'),
        prazo_retorno: $('#prazo_retorno').val() || null
    };

    const url = id ? `/contratos/api/tramitacoes/${id}/` : '/contratos/api/tramitacoes/';
    const method = id ? 'PUT' : 'POST';

    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(data),
        headers: { 'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val() },
        success: function() {
            $('#modal-tramitacao').modal('hide');
            carregarContratacoesCards();
            if ($.fn.DataTable.isDataTable('#tabela-tramitacoes')) {
                $('#tabela-tramitacoes').DataTable().ajax.reload(null, false);
            }
            Swal.fire('Sucesso!', 'Tramitação registrada.', 'success');
        },
        error: function(xhr) {
            console.error(xhr.responseText);
            Swal.fire('Erro!', 'Não foi possível registrar a tramitação.', 'error');
        }
    });
}

// --- Funções de Cronograma ---

function abrirModalCronograma(id) {
    $('#crono_contratacao_id').val(id);
    
    // Limpa a tabela
    $('#tabela-fases-crono tbody tr').each(function() {
        $(this).find('.prazo-crono').val('');
        $(this).find('.real-crono').val('');
        $(this).find('.status-crono').text('-');
    });

    $.get(`/contratos/api/processos/${id}/`, function(data) {
        if (data.cronogramas && data.cronogramas.length > 0) {
            data.cronogramas.forEach(crono => {
                let row = $(`#tabela-fases-crono tbody tr[data-fase="${crono.fase_artefato}"]`);
                if (row.length) {
                    row.find('.prazo-crono').val(crono.prazo_entrega);
                    row.find('.real-crono').val(crono.data_entrega_real);
                    
                    let statusBadge = '';
                    if (crono.status === 'No Prazo') statusBadge = '<span class="badge bg-success">No Prazo</span>';
                    else if (crono.status === 'Atrasado') statusBadge = '<span class="badge bg-danger">Atrasado</span>';
                    else if (crono.status === 'Entregue') statusBadge = '<span class="badge bg-primary">Entregue</span>';
                    
                    row.find('.status-crono').html(statusBadge);
                }
            });
        }
        $('#modal-cronograma').modal('show');
    });
}

function gerarCronogramaAutomatico() {
    const id = $('#crono_contratacao_id').val();
    if (!id) return;

    Swal.fire({
        title: 'Gerar Cronograma Padrão?',
        text: "Isso irá sobrescrever todas as datas atuais com base na prioridade desta contratação.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, gerar!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            $.post(`/contratos/api/processos/${id}/gerar-cronograma/`, {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            }, function(response) {
                Swal.fire('Gerado!', 'O cronograma padrão foi preenchido.', 'success');
                abrirModalCronograma(id); // Recarrega os dados na tela
                carregarContratacoesCards();
            }).fail(function(err) {
                Swal.fire('Erro', 'Não foi possível gerar o cronograma.', 'error');
            });
        }
    });
}

function salvarCronograma() {
    const id = $('#crono_contratacao_id').val();
    if (!id) return;
    
    let cronogramaData = [];
    $('#tabela-fases-crono tbody tr').each(function() {
        const fase = $(this).data('fase');
        const prazo = $(this).find('.prazo-crono').val();
        const real = $(this).find('.real-crono').val();
        
        if (prazo || real) {
            cronogramaData.push({
                fase_artefato: fase,
                prazo_entrega: prazo || null,
                data_entrega_real: real || null
            });
        }
    });
    
    $.ajax({
        url: `/contratos/api/processos/${id}/atualizar-cronograma/`,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({ cronograma: cronogramaData }),
        headers: {
            'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function() {
            Swal.fire('Salvo!', 'O cronograma foi atualizado com sucesso.', 'success');
            $('#modal-cronograma').modal('hide');
            carregarContratacoesCards();
        },
        error: function(err) {
            Swal.fire('Erro', 'Ocorreu um erro ao salvar.', 'error');
        }
    });
}

function formatDateToLocal(dateStr) {
    if (!dateStr) return '';
    const parts = dateStr.split('-');
    if (parts.length === 3) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }
    return dateStr;
}

function formatTimeline(rowData) {
    let cronogramas = rowData.cronogramas || [];
    
    // Default phases in order
    const defaultPhases = ['ETP', 'TR', 'PESQUISA', 'JURIDICO', 'EDITAL'];
    const phaseNames = {
        'ETP': 'ETP',
        'TR': 'TR',
        'PESQUISA': 'Pesquisa',
        'JURIDICO': 'Jurídico',
        'EDITAL': 'Edital'
    };

    let stepperHtml = '<div class="timeline-container"><div class="stepper">';
    
    defaultPhases.forEach((fase, index) => {
        let crono = cronogramas.find(c => c.fase_artefato === fase);
        let statusClass = '';
        let iconHtml = index + 1;
        let dateText = '-';

        if (crono) {
            if (crono.status === 'Entregue') {
                statusClass = 'completed';
                iconHtml = '<i class="bi bi-check-lg"></i>';
                dateText = crono.data_entrega_real ? formatDateToLocal(crono.data_entrega_real) : 'Entregue';
            } else if (crono.status === 'Atrasado') {
                statusClass = 'delayed';
                iconHtml = '<i class="bi bi-exclamation-lg"></i>';
                dateText = '<span class="text-danger fw-bold">Atrasado: ' + formatDateToLocal(crono.prazo_entrega) + '</span>';
            } else {
                dateText = 'Prev: ' + formatDateToLocal(crono.prazo_entrega);
            }
        } else {
             dateText = 'Não Iniciado';
        }

        stepperHtml += `
            <div class="stepper-item ${statusClass}">
                <div class="stepper-circle">${iconHtml}</div>
                <div class="stepper-label">${phaseNames[fase]}</div>
                <div class="stepper-date">${dateText}</div>
            </div>
        `;
    });

    stepperHtml += '</div>';
    return stepperHtml;
}

// --- Funções de Renderização (List View) ---
function carregarContratacoesCards() {
    const grid = $('#contratacoes-grid');
    grid.html(`
        <div class="col-12 text-center py-5" id="contratacoes-loading">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2 text-muted fw-bold">Carregando processos...</p>
        </div>
    `);

    $.get('/contratos/api/processos/', function(data) {
        // Ordena os processos pelo valor (maior para menor) para os cards acompanharem o gráfico
        data.sort((a, b) => {
            const valA = parseFloat(a.valor_previsto) || 0;
            const valB = parseFloat(b.valor_previsto) || 0;
            return valB - valA;
        });

        window.processosGlobais = data;
        grid.empty();
        
        // Renderiza o gráfico de valores
        renderizarGraficoValores(data);
        
        if (!data || data.length === 0) {
            grid.html('<div class="col-12 text-center py-5"><p class="text-muted fs-5">Nenhum processo encontrado.</p></div>');
            $('#timeline-list').html('<div class="text-center py-5 text-muted"><p>Nenhum cronograma ativo.</p></div>');
            return;
        }

        $('#timeline-list').empty();

        data.forEach(processo => {
            
            let statusCronoBadge = `<span class="badge bg-secondary">${processo.status_cronograma || 'Sem Cronograma'}</span>`;
            if (processo.status_cronograma === 'No Prazo') statusCronoBadge = '<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i>No Prazo</span>';
            if (processo.status_cronograma === 'Atrasado') statusCronoBadge = '<span class="badge bg-danger"><i class="bi bi-exclamation-circle me-1"></i>Atrasado</span>';

            let ultimaTramitacaoHtml = `
                <div class="d-flex flex-column align-items-center justify-content-center bg-light rounded border h-100 text-muted py-2" style="border-style: dashed !important; min-height: 80px;">
                    <i class="bi bi-inbox fs-5 mb-1 opacity-50"></i>
                    <span style="font-size: 0.8rem;">Nenhuma tramitação registrada</span>
                </div>
            `;
            if (processo.tramitacoes && processo.tramitacoes.length > 0) {
                // clona e ordena por data_entrada decrescente
                const tramitacoesSorted = [...processo.tramitacoes].sort((a, b) => new Date(b.data_entrada) - new Date(a.data_entrada));
                const u = tramitacoesSorted[0];
                
                const resumoMotivo = u.motivo ? `<div class="mt-1 text-dark" style="font-size: 0.8rem;"><i class="bi bi-file-text text-secondary me-1"></i> <strong>Despacho:</strong> ${u.motivo}</div>` : '';
                const responsavel = u.atualizado_por_nome || 'Sistema';
                const dataAtualizacao = u.updated_at ? formatDateToLocal(u.updated_at.substring(0, 10)) : formatDateToLocal(u.data_entrada);
                
                const infoAssinatura = u.unidade_ultima_assinatura ? `<div class="text-muted mt-1" style="font-size: 0.75rem;"><i class="bi bi-pen me-1"></i>Enviado por <strong>${u.unidade_ultima_assinatura}</strong> ${u.data_ultima_movimentacao ? 'em ' + formatDateToLocal(u.data_ultima_movimentacao) : ''}</div>` : '';
                
                ultimaTramitacaoHtml = `
                    <div class="d-flex flex-column bg-light p-2 rounded border h-100">
                        <div class="d-flex flex-wrap align-items-center justify-content-between mb-1">
                            <span class="badge bg-danger shadow-sm py-1"><i class="bi bi-geo-alt-fill me-1"></i> ${u.unidade_atual}</span>
                            <span class="text-muted fw-bold" style="font-size: 0.75rem;"><i class="bi bi-calendar-event me-1"></i>Chegou em ${formatDateToLocal(u.data_entrada)}</span>
                        </div>
                        ${infoAssinatura}
                        ${resumoMotivo}
                        <div class="mt-auto pt-1 text-muted text-end" style="font-size: 0.7rem;">
                            <i class="bi bi-person-circle me-1"></i> Atualizado por <strong>${responsavel}</strong> em ${dataAtualizacao}
                        </div>
                    </div>
                `;
            }

            const listItemHtml = `
                <div class="col-12" style="cursor: pointer;" onclick="abrirModalDetalhesProcesso(${processo.id})">
                    <div class="bg-white rounded-3 shadow-sm border p-3 transition-hover">
                        
                        <div class="row gx-3">
                            <!-- Esquerda: Info do Processo -->
                            <div class="col-lg-5 col-xl-4 d-flex flex-column">
                                <div class="d-flex flex-wrap gap-2 mb-1">
                                    ${statusCronoBadge}
                                    ${processo.esta_no_pac ? '<span class="badge bg-success py-1"><i class="bi bi-check-circle me-1"></i>PAC</span>' : ''}
                                    ${processo.eleicoes_ano_corrente ? '<span class="badge bg-warning text-dark py-1"><i class="bi bi-box2-heart me-1"></i>Eleições</span>' : ''}
                                </div>
                                
                                <h6 class="mb-1 fw-bold text-primary d-flex align-items-center gap-1" style="letter-spacing: -0.3px;">
                                    ${processo.numero_processo}
                                    <button class="btn btn-sm btn-light text-secondary border-0 p-0 px-1 rounded-1" onclick="event.stopPropagation(); navigator.clipboard.writeText('${processo.numero_processo}'); Swal.fire({toast: true, position: 'top-end', icon: 'success', title: 'Copiado!', showConfirmButton: false, timer: 1500});" title="Copiar número do processo">
                                        <i class="bi bi-copy" style="font-size: 0.8rem;"></i>
                                    </button>
                                </h6>
                                
                                <p class="text-muted small mb-1" style="font-size: 0.8rem;">
                                    <i class="bi bi-building me-1"></i>${processo.unidade_responsavel || 'Sem Unidade'} 
                                    <span class="mx-1">|</span> 
                                    <strong>Fase:</strong> <span class="text-info">${processo.fase_display || processo.fase}</span>
                                </p>
                                
                                <p class="mb-0 text-dark" style="font-size: 0.85rem; line-height: 1.3;">${processo.objeto || 'Objeto não descrito'}</p>
                            </div>

                            <!-- Direita: Última Tramitação -->
                            <div class="col-lg-7 col-xl-8 mt-2 mt-lg-0">
                                ${ultimaTramitacaoHtml}
                            </div>
                        </div>

                        <hr class="text-muted opacity-25 my-2">

                        <!-- Rodapé: Botões -->
                        <div class="d-flex justify-content-end gap-2">
                            <button class="btn btn-sm btn-outline-info fw-bold py-1 px-2" style="font-size: 0.8rem;" onclick="event.stopPropagation(); abrirModalCronograma(${processo.id})">
                                <i class="bi bi-calendar-check me-1"></i>Cronograma
                            </button>
                            <button class="btn btn-sm btn-outline-primary fw-bold py-1 px-2" style="font-size: 0.8rem;" onclick="event.stopPropagation(); editarContratacao(${processo.id})">
                                <i class="bi bi-pencil me-1"></i>Editar Processo
                            </button>
                        </div>

                    </div>
                </div>
            `;
            grid.append(listItemHtml);

            // Adicionar ao Timeline List (Top Dashboard)
            let badgeCompact = statusCronoBadge.replace('badge', 'badge rounded-pill').replace('px-2', 'px-1').replace('py-1', '');
            const timelineItem = `
                <div class="mb-3 border-bottom pb-2">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="fw-bold text-primary" style="font-size: 0.85rem;">${processo.numero_processo}</span>
                        ${badgeCompact}
                    </div>
                    <p class="text-muted mb-2 text-truncate" style="font-size: 0.75rem;" title="${processo.objeto}">${processo.objeto || 'Objeto não descrito'}</p>
                    <div class="px-1">
                        ${formatTimeline(processo)}
                    </div>
                </div>
            `;
            $('#timeline-list').append(timelineItem);
        });
    }).fail(function() {
        grid.html('<div class="col-12 text-center py-5 text-danger"><p>Erro ao carregar processos.</p></div>');
        $('#timeline-list').html('<div class="text-center py-5 text-danger"><p>Erro ao carregar.</p></div>');
    });
}

// --- Gráfico de Valores ---
function renderizarGraficoValores(processos) {
    if (!processos || processos.length === 0) return;
    
    // Filtrar processos que tem valor > 0
    let processosComValor = processos.filter(p => p.valor_previsto && parseFloat(p.valor_previsto) > 0);
    
    // Ordenar do MAIOR para o MENOR
    processosComValor.sort((a, b) => parseFloat(b.valor_previsto) - parseFloat(a.valor_previsto));
    
    // Limitar aos top 15 se houver muitos, para não quebrar o layout
    if (processosComValor.length > 15) {
        processosComValor = processosComValor.slice(0, 15);
    }
    
    let categorias = processosComValor.map(p => {
        let title = p.objeto || p.numero_processo;
        return title.length > 40 ? title.substring(0, 40) + '...' : title;
    });
    
    let valores = processosComValor.map(p => parseFloat(p.valor_previsto));

    var options = {
        series: [{
            name: 'Valor Estimado',
            data: valores
        }],
        chart: {
            type: 'bar',
            height: Math.max(450, categorias.length * 40),
            toolbar: { show: false },
            parentHeightOffset: 0
        },
        plotOptions: {
            bar: {
                borderRadius: 4,
                horizontal: true,
                dataLabels: {
                    position: 'top',
                },
                barHeight: '65%'
            }
        },
        colors: ['#0dcaf0'],
        dataLabels: {
            enabled: true,
            textAnchor: 'start',
            style: {
                colors: ['#495057'],
                fontSize: '11px',
                fontWeight: 600
            },
            formatter: function (val, opt) {
                return val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            },
            offsetX: 5
        },
        xaxis: {
            categories: categorias,
            labels: {
                formatter: function (val) {
                    if (val >= 1000000) return "R$ " + (val/1000000).toFixed(1) + "M";
                    if (val >= 1000) return "R$ " + (val/1000).toFixed(0) + "k";
                    return "R$ " + val;
                },
                style: {
                    colors: '#6c757d'
                }
            },
            axisBorder: { show: false },
            axisTicks: { show: false }
        },
        yaxis: {
            labels: {
                style: {
                    colors: '#495057',
                    fontSize: '11px',
                    fontWeight: 500
                },
                maxWidth: 200
            }
        },
        tooltip: {
            theme: 'light',
            y: {
                formatter: function (val) {
                    return val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                }
            }
        },
        grid: {
            borderColor: '#f1f3f5',
            strokeDashArray: 4,
            xaxis: { lines: { show: true } },
            yaxis: { lines: { show: false } },
        }
    };

    if (window.chartValores) {
        window.chartValores.destroy();
    }
    const chartContainer = document.querySelector("#chart-valores");
    if (chartContainer) {
        window.chartValores = new ApexCharts(chartContainer, options);
        window.chartValores.render();
    }
}

// --- Detalhes do Processo (Modal) ---
function abrirModalDetalhesProcesso(id) {
    if (!window.processosGlobais) return;
    const proc = window.processosGlobais.find(p => p.id === id);
    if (!proc) return;
    
    // Título
    $('#detalheNumero').html(`<i class="bi bi-diagram-3 me-2"></i> ${proc.numero_processo}`);
    
    // Badges
    let badgesHtml = '';
    if (proc.esta_no_pac) badgesHtml += '<span class="badge bg-success fs-6"><i class="bi bi-check-circle me-1"></i>PAC</span>';
    if (proc.eleicoes_ano_corrente) badgesHtml += '<span class="badge bg-warning text-dark fs-6"><i class="bi bi-box2-heart me-1"></i>Eleições</span>';
    
    let badgeCrono = '<span class="badge bg-secondary fs-6">Sem Cronograma</span>';
    if (proc.status_cronograma === 'No Prazo') badgeCrono = '<span class="badge bg-success fs-6"><i class="bi bi-check-circle me-1"></i>No Prazo</span>';
    if (proc.status_cronograma === 'Atrasado') badgeCrono = '<span class="badge bg-danger fs-6"><i class="bi bi-exclamation-circle me-1"></i>Atrasado</span>';
    badgesHtml += badgeCrono;
    
    $('#detalheBadges').html(badgesHtml);
    
    // Dados Básicos
    $('#detalheObjeto').text(proc.objeto || '-');
    $('#detalheDescricao').text(proc.descricao_objeto || '-');
    $('#detalheJustificativa').text(proc.justificativa || '-');
    $('#detalheObservacoes').text(proc.observacoes || '-');
    
    $('#detalheUnidade').html(`<i class="bi bi-building me-1 text-muted"></i> ${proc.unidade_responsavel || '-'}`);
    $('#detalheServidor').html(`<i class="bi bi-person me-1 text-muted"></i> ${proc.servidor_responsavel || '-'}`);
    $('#detalheFase').text(proc.fase_display || proc.fase || '-');
    $('#detalhePrioridade').html(`<span class="badge bg-info text-dark">${proc.prioridade || 'Média'}</span>`);
    
    const valPrev = parseFloat(proc.valor_previsto || 0);
    $('#detalheValor').text(valPrev.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }));
    
    $('#detalheConclusao').text(proc.data_prevista_conclusao ? formatDateToLocal(proc.data_prevista_conclusao) : '-');
    
    // Cronograma
    $('#detalheCronograma').html(formatTimeline(proc));
    
    // Tramitações
    let tramitacoesHtml = '<p class="text-muted"><i class="bi bi-info-circle me-1"></i> Nenhuma tramitação SEI registrada.</p>';
    if (proc.tramitacoes && proc.tramitacoes.length > 0) {
        const tramitacoesSorted = [...proc.tramitacoes].sort((a, b) => new Date(b.data_entrada) - new Date(a.data_entrada));
        
        tramitacoesHtml = tramitacoesSorted.map(t => {
            const dateStr = formatDateToLocal(t.data_entrada);
            const content = t.motivo ? `<div class="mt-2 text-dark"><strong>Despacho:</strong> ${t.motivo}</div>` : '';
            const assinatura = t.unidade_ultima_assinatura ? `<div class="mt-1 text-muted small"><i class="bi bi-pen me-1"></i>Assinado/Enviado por: ${t.unidade_ultima_assinatura} ${t.data_ultima_movimentacao ? '(' + formatDateToLocal(t.data_ultima_movimentacao) + ')' : ''}</div>` : '';
            
            return `
                <div class="mb-3 border-start border-3 border-danger ps-3 pb-2 position-relative">
                    <button class="btn btn-sm btn-light border shadow-sm position-absolute top-0 end-0 rounded-circle" onclick="editarTramitacao(${t.id}, ${proc.id})" title="Editar Tramitação" style="padding: 2px 6px; z-index: 10;">
                        <i class="bi bi-pencil text-primary" style="font-size: 0.75rem;"></i>
                    </button>
                    <div class="d-flex justify-content-between align-items-center mb-1 pe-4">
                        <span class="fw-bold text-dark"><i class="bi bi-geo-alt-fill me-1 text-danger"></i>${t.unidade_atual}</span>
                        <span class="badge bg-light text-dark border"><i class="bi bi-calendar me-1"></i> Chegada em ${dateStr}</span>
                    </div>
                    ${assinatura}
                    ${content}
                </div>
            `;
        }).join('');
    }
    $('#detalheTramitacoes').html(tramitacoesHtml);
    
    // Mostrar Modal
    new bootstrap.Modal(document.getElementById('modalDetalhesProcesso')).show();
}
