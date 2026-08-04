document.addEventListener("DOMContentLoaded", function() {
    initDataTables();
    carregarMétricas();
    carregarWidgetPendencias();
});

function initDataTables() {
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

    $('#tabela-solicitacoes').DataTable({
        responsive: true,
        ajax: {
            url: '/reembolsos/api/solicitacoes/',
            dataSrc: ''
        },
        columns: [
            { data: 'id' },
            { data: 'servidor_nome' },
            { 
                data: null,
                render: function(data, type, row) {
                    const ini = row.periodo_inicio ? moment(row.periodo_inicio).format('DD/MM/YYYY') : '-';
                    const fim = row.periodo_fim ? moment(row.periodo_fim).format('DD/MM/YYYY') : '-';
                    return `${ini} a ${fim}`;
                }
            },
            { 
                data: 'status',
                render: function(data) {
                    const dict = {
                        'em_analise': 'Em Análise',
                        'pendente': 'Pendente',
                        'enviado': 'Enviado',
                        'aprovada': 'Aprovada',
                        'concluido': 'Concluído',
                        'negada': 'Negada'
                    };
                    return `<span class="status-badge status-${data}">${dict[data]}</span>`;
                }
            },
            { 
                data: 'valor_ressarcido',
                render: function(data) {
                    if(!data) return '-';
                    return `R$ ${parseFloat(data).toFixed(2).replace('.', ',')}`;
                }
            },
            {
                data: 'id',
                className: 'text-end',
                render: function(data, type, row) {
                    return `
                        <button class="btn btn-sm btn-outline-secondary" onclick="imprimirRelatorioSolicitacao(${data})" title="Imprimir Solicitação"><i class="bi bi-printer"></i></button>
                        <button class="btn btn-sm btn-outline-primary ms-1" onclick="editarSolicitacao(${data})"><i class="bi bi-pencil"></i></button>
                        <button class="btn btn-sm btn-outline-danger" onclick="excluirSolicitacao(${data})"><i class="bi bi-trash"></i></button>
                    `;
                }
            }
        ],
        language: {
            "sEmptyTable": "Nenhum registro encontrado",
            "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros",
            "sInfoEmpty": "Mostrando 0 até 0 de 0 registros",
            "sInfoFiltered": "(Filtrados de _MAX_ registros)",
            "sLengthMenu": "Mostrar _MENU_ resultados por página",
            "sLoadingRecords": "Carregando...",
            "sProcessing": "Processando...",
            "sZeroRecords": "Nenhum registro encontrado",
            "sSearch": "Pesquisar:",
            "oPaginate": {
                "sNext": "Próximo",
                "sPrevious": "Anterior",
                "sFirst": "Primeiro",
                "sLast": "Último"
            }
        },
        order: [[0, 'desc']],
        orderCellsTop: true,
        initComplete: function() {
            aplicarFiltroColunas(this.api());
        }
    });

    $('#tabela-servidores').DataTable({
        responsive: true,
        ajax: {
            url: '/reembolsos/api/servidores/',
            dataSrc: ''
        },
        columns: [
            { data: 'nome' },
            { data: 'cargo' },
            {
                data: 'ativo',
                render: function(data) {
                    return data 
                        ? `<span class="badge bg-success">Ativo</span>` 
                        : `<span class="badge bg-secondary">Inativo</span>`;
                }
            },
            { data: 'telefone_linha', className: 'format-telefone' },
            { 
                data: 'teto_ressarcimento',
                render: function(data) { return `R$ ${parseFloat(data).toFixed(2).replace('.', ',')}`; }
            },
            {
                data: 'id',
                className: 'text-end',
                render: function(data, type, row) {
                    return `
                        <button class="btn btn-sm btn-outline-secondary" onclick="imprimirRelatorioAnual(${data})" title="Imprimir Relatório Anual"><i class="bi bi-printer"></i></button>
                        <button class="btn btn-sm btn-outline-primary ms-1" onclick="editarServidor(${data})"><i class="bi bi-pencil"></i></button>
                        <button class="btn btn-sm btn-outline-danger" onclick="excluirServidor(${data})"><i class="bi bi-trash"></i></button>
                    `;
                }
            }
        ],
        language: {
            "sEmptyTable": "Nenhum registro encontrado",
            "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros",
            "sInfoEmpty": "Mostrando 0 até 0 de 0 registros",
            "sInfoFiltered": "(Filtrados de _MAX_ registros)",
            "sLengthMenu": "Mostrar _MENU_ resultados por página",
            "sLoadingRecords": "Carregando...",
            "sProcessing": "Processando...",
            "sZeroRecords": "Nenhum registro encontrado",
            "sSearch": "Pesquisar:",
            "oPaginate": {
                "sNext": "Próximo",
                "sPrevious": "Anterior",
                "sFirst": "Primeiro",
                "sLast": "Último"
            }
        },
        orderCellsTop: true,
        initComplete: function() {
            aplicarFiltroColunas(this.api());
        }
    });
}

async function carregarMétricas() {
    try {
        const reqServ = await fetch('/reembolsos/api/servidores/');
        const reqSol = await fetch('/reembolsos/api/solicitacoes/');
        if(reqServ.ok && reqSol.ok) {
            const servidores = await reqServ.json();
            const solicitacoes = await reqSol.json();
            
            // 1. Servidores Ativos (cadastrados)
            const servidoresAtivos = servidores.filter(s => s.ativo === true);
            document.getElementById('metric-servidores').textContent = servidoresAtivos.length;
            
            // 2 e 3. Calcular Total Ano e Solicitações Atendidas
            let atendidas = 0;
            let totalAno = 0;
            const anoAtual = new Date().getFullYear();
            
            // 4. Valor Reembolsado Mês (com base no filtro)
            const inputMes = document.getElementById('filtro-mes');
            if(!inputMes.value) {
                const mesAtual = new Date().getMonth() + 1;
                inputMes.value = `${anoAtual}-${mesAtual.toString().padStart(2, '0')}`;
            }
            const [filtroAno, filtroMes] = inputMes.value.split('-');
            let totalMes = 0;
            
            solicitacoes.forEach(s => {
                if(s.status === 'aprovada' || s.status === 'concluido') {
                    const dataFim = new Date(s.periodo_fim);
                    const ano = dataFim.getFullYear();
                    const mes = dataFim.getMonth() + 1;
                    
                    if(ano === anoAtual) {
                        atendidas++;
                        totalAno += parseFloat(s.valor_ressarcido || 0);
                    }
                    
                    if(ano === parseInt(filtroAno) && mes === parseInt(filtroMes)) {
                        totalMes += parseFloat(s.valor_ressarcido || 0);
                    }
                }
            });

            // (lógica de alerta bancário migrada para carregarWidgetPendencias())
            
            // 5. Saldo Disponível no Ano (Soma Teto Servidores * 12 - Total Ano)
            let somaTeto = 0;
            servidores.forEach(s => {
                if (s.ativo) {
                    somaTeto += parseFloat(s.teto_ressarcimento || 0);
                }
            });
            const totalEmpenhado = somaTeto * 12;
            const saldoDisponivel = totalEmpenhado - totalAno;
            
            // Atualizar DOM
            document.getElementById('metric-atendidas').textContent = atendidas;
            document.getElementById('metric-ano').textContent = `R$ ${totalAno.toFixed(2).replace('.', ',')}`;
            document.getElementById('metric-mes').textContent = `R$ ${totalMes.toFixed(2).replace('.', ',')}`;
            document.getElementById('metric-empenhado').textContent = `R$ ${totalEmpenhado.toFixed(2).replace('.', ',')}`;
            document.getElementById('metric-saldo').textContent = `R$ ${saldoDisponivel.toFixed(2).replace('.', ',')}`;
        }
    } catch(e) { console.error(e); }
}

// ---------------------- WIDGET DE PENDÊNCIAS ----------------------
async function carregarWidgetPendencias() {
    try {
        const res = await fetch('/reembolsos/api/solicitacoes/');
        if (!res.ok) return;
        const solicitacoes = await res.json();

        // Status que NÃO estão concluídos
        const statusPendente = ['em_analise', 'pendente', 'enviado', 'aprovada'];
        const pendentes = solicitacoes
            .filter(s => statusPendente.includes(s.status))
            .sort((a, b) => new Date(b.criado_em || 0) - new Date(a.criado_em || 0));

        const badge = document.getElementById('badge-recebidas-count');
        const listGroup = document.getElementById('lista-recebidas-dashboard');
        const card = document.getElementById('card-widget-recebidas');
        const titulo = document.getElementById('titulo-widget-recebidas');
        const rodape = document.getElementById('rodape-widget-recebidas');

        badge.textContent = pendentes.length;
        listGroup.innerHTML = '';

        if (pendentes.length === 0) {
            listGroup.innerHTML = '<div class="text-center text-muted py-2"><i class="bi bi-emoji-smile me-2"></i>Nenhuma solicitação pendente! Tudo em dia.</div>';
            card.className = 'card shadow-sm border-0 interactive-card';
            card.style.backgroundColor = '';
            titulo.className = 'fw-bold mb-0 text-success';
            titulo.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>Status: Tudo em Dia';
            badge.className = 'badge bg-success rounded-pill shadow-sm';
            rodape.style.display = 'none';
            return;
        }

        // Estilo de alerta
        card.className = 'card shadow-sm border-0 interactive-card widget-recebidas-alerta';
        titulo.className = 'fw-bold mb-0 text-danger';
        titulo.innerHTML = '<i class="bi bi-exclamation-triangle-fill me-2 pulse-icon"></i>Atenção: Demandas Pendentes';
        badge.className = 'badge bg-danger rounded-pill pulse-badge shadow-sm';
        rodape.style.display = 'block';

        const statusLabels = {
            'em_analise': 'Em Análise',
            'pendente': 'Pendente',
            'enviado': 'Enviado',
            'aprovada': 'Aprovada',
        };
        const statusColors = {
            'em_analise': '#856404',
            'pendente': '#fd7e14',
            'enviado': '#0d6efd',
            'aprovada': '#198754',
        };

        // Exibe até 3 mais recentes
        const max = Math.min(pendentes.length, 3);
        for (let i = 0; i < max; i++) {
            const s = pendentes[i];
            const dataStr = s.criado_em || '';
            let dataFormatada = '-';
            if (dataStr) {
                const d = new Date(dataStr);
                dataFormatada = d.toLocaleDateString('pt-BR');
            }
            const servidor = s.servidor_nome || '-';
            const statusLabel = statusLabels[s.status] || s.status;
            const statusColor = statusColors[s.status] || '#6c757d';
            const protocolo = s.protocolo_sei || 'Sem protocolo';

            listGroup.innerHTML += `
                <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2 mb-1 rounded" style="background-color: #fff5f5; border: 1px solid #ffcaca;">
                    <div>
                        <small class="text-danger d-block mb-0 fw-bold" style="font-size: 0.8rem;"><i class="bi bi-clock-history"></i> Data: ${dataFormatada}</small>
                        <span class="fw-bold text-dark">${servidor}</span>
                        <span class="badge ms-1" style="font-size: 0.7rem; background-color: ${statusColor}; color: #fff;">${statusLabel}</span>
                        <br><span class="text-muted" style="font-size: 0.85rem;">SEI: ${protocolo}</span>
                    </div>
                    <i class="bi bi-chevron-right text-danger fw-bold fs-5"></i>
                </div>
            `;
        }

    } catch (e) {
        console.error('Erro ao carregar widget de pendências:', e);
        const listGroup = document.getElementById('lista-recebidas-dashboard');
        if (listGroup) listGroup.innerHTML = '<div class="text-center text-danger py-3">Erro ao carregar.</div>';
    }
}

// ---------------------- MODAL DE PENDÊNCIAS ----------------------
const statusLabelsGlobal = {
    'em_analise': 'Em Análise',
    'pendente': 'Pendente',
    'enviado': 'Enviado',
    'aprovada': 'Aprovada',
};
const statusBadgeColors = {
    'em_analise': 'bg-warning text-dark',
    'pendente': 'bg-orange text-white',
    'enviado': 'bg-primary',
    'aprovada': 'bg-success',
};

async function abrirModalPendencias() {
    // Abre o modal imediatamente
    const modal = new bootstrap.Modal(document.getElementById('modal-lista-pendencias'));
    modal.show();

    const tbody = document.getElementById('corpo-tabela-pendencias');
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4">
        <div class="spinner-border text-danger" role="status"></div>
        <p class="mt-2 text-muted">Carregando pendências...</p>
    </td></tr>`;

    try {
        const res = await fetch('/reembolsos/api/solicitacoes/');
        if (!res.ok) throw new Error('Erro ao buscar dados');
        const solicitacoes = await res.json();

        const statusPendente = ['em_analise', 'pendente', 'enviado', 'aprovada'];
        const pendentes = solicitacoes
            .filter(s => statusPendente.includes(s.status))
            .sort((a, b) => new Date(b.criado_em || 0) - new Date(a.criado_em || 0));

        document.getElementById('modal-badge-pendencias').textContent = pendentes.length;

        if (pendentes.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-success">
                <i class="bi bi-check-circle-fill fs-3"></i>
                <p class="mt-2">Nenhuma pendência! Tudo em dia.</p>
            </td></tr>`;
            return;
        }

        tbody.innerHTML = '';
        pendentes.forEach(s => {
            const data = s.criado_em ? new Date(s.criado_em).toLocaleDateString('pt-BR') : '-';
            const statusLabel = statusLabelsGlobal[s.status] || s.status;
            const badgeCls = statusBadgeColors[s.status] || 'bg-secondary';
            const ressarcimento = s.valor_ressarcido ? `R$ ${parseFloat(s.valor_ressarcido).toFixed(2).replace('.', ',')}` : '-';
            const sei = s.protocolo_sei || '-';

            tbody.innerHTML += `
                <tr>
                    <td class="fw-bold">${s.servidor_nome || '-'}</td>
                    <td>${data}</td>
                    <td><span class="badge ${badgeCls}">${statusLabel}</span></td>
                    <td>${sei}</td>
                    <td>${ressarcimento}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="visualizarSolicitacaoPendencia(${s.id})" title="Visualizar">
                            <i class="bi bi-eye"></i> Ver
                        </button>
                        <button class="btn btn-sm btn-success" onclick="concluirSolicitacaoPendencia(${s.id})" title="Concluir">
                            <i class="bi bi-check-lg"></i> Concluir
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch(e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-3">Erro ao carregar pendências.</td></tr>`;
    }
}

async function visualizarSolicitacaoPendencia(id) {
    // Fecha modal de pendências e abre o de solicitação em modo visualização
    bootstrap.Modal.getInstance(document.getElementById('modal-lista-pendencias'))?.hide();
    await visualizarSolicitacao(id);
}

async function visualizarSolicitacao(id) {
    try {
        const res = await fetch(`/reembolsos/api/solicitacoes/${id}/`);
        if(res.ok) {
            const data = await res.json();
            
            document.getElementById('vis-solicitacao-servidor').innerText = data.servidor_nome || '-';
            document.getElementById('vis-solicitacao-sei').innerText = data.protocolo_sei || '-';
            
            // Faturas
            const tbFaturas = document.getElementById('vis-faturas-tbody');
            tbFaturas.innerHTML = '';
            if (data.faturas && data.faturas.length > 0) {
                data.faturas.forEach(f => {
                    const ini = f.periodo_inicio ? moment(f.periodo_inicio).format('DD/MM/YYYY') : '-';
                    const fim = f.periodo_fim ? moment(f.periodo_fim).format('DD/MM/YYYY') : '-';
                    const valorFat = f.valor_fatura ? `R$ ${parseFloat(f.valor_fatura).toFixed(2).replace('.', ',')}` : '-';
                    const valorServ = f.valor_servico ? `R$ ${parseFloat(f.valor_servico).toFixed(2).replace('.', ',')}` : '-';
                    const badge = (f.aprovada === true || f.aprovada === 'true') 
                                    ? '<span class="badge bg-success">Sim</span>' 
                                    : `<span class="badge bg-danger">Não</span><div class="small text-danger mt-1">${f.justificativa_negacao || ''}</div>`;
                    
                    tbFaturas.innerHTML += `
                        <tr>
                            <td>${ini} a ${fim}</td>
                            <td>${valorFat}</td>
                            <td>${valorServ}</td>
                            <td>${f.doc_fatura || '-'}</td>
                            <td>${f.doc_comprovante || '-'}</td>
                            <td>${badge}</td>
                        </tr>
                    `;
                });
            } else {
                tbFaturas.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nenhuma fatura anexada.</td></tr>';
            }

            document.getElementById('vis-solicitacao-ob').innerText = data.protocolo_ordem_bancaria || '-';
            let dtPag = '-';
            if (data.data_pagamento) {
                dtPag = moment(data.data_pagamento).format('DD/MM/YYYY');
            }
            document.getElementById('vis-solicitacao-data-pag').innerText = dtPag;
            
            const badgeMap = {
                'em_analise': {label: 'Em Análise', class: 'bg-warning text-dark'},
                'pendente': {label: 'Pendente', class: 'bg-warning text-dark'},
                'enviado': {label: 'Enviado', class: 'bg-primary'},
                'aprovada': {label: 'Aprovada', class: 'bg-success'},
                'concluido': {label: 'Concluído', class: 'bg-success'},
                'negada': {label: 'Negada', class: 'bg-danger'}
            };
            
            const st = badgeMap[data.status] || {label: data.status, class: 'bg-secondary'};
            const statusEl = document.getElementById('vis-solicitacao-status');
            statusEl.className = `badge fs-6 ${st.class}`;
            statusEl.innerText = st.label;

            // Observações
            const obsList = document.getElementById('vis-observacoes-list');
            obsList.innerHTML = '';
            if (data.observacoes) {
                const obsArray = data.observacoes.split('|||').filter(txt => txt.trim());
                if (obsArray.length > 0) {
                    obsArray.forEach(txt => {
                        obsList.innerHTML += `<li class="list-group-item bg-transparent text-secondary"><i class="bi bi-chevron-right me-2 text-muted"></i>${txt.trim()}</li>`;
                    });
                } else {
                    obsList.innerHTML = '<li class="list-group-item bg-transparent text-muted text-center border-0">Nenhuma observação.</li>';
                }
            } else {
                obsList.innerHTML = '<li class="list-group-item bg-transparent text-muted text-center border-0">Nenhuma observação.</li>';
            }

            const modal = new bootstrap.Modal(document.getElementById('modal-visualizar-solicitacao'));
            modal.show();
        }
    } catch(e) { console.error(e); }
}

async function concluirSolicitacaoPendencia(id) {
    // Fecha modal de pendências e abre o de solicitação com status focado em "Concluído"
    bootstrap.Modal.getInstance(document.getElementById('modal-lista-pendencias'))?.hide();
    await editarSolicitacao(id, true);
}


async function popularSelectLimites() {
    try {
        const res = await fetch('/reembolsos/api/limites/');
        if(res.ok) {
            const data = await res.json();
            const select = document.getElementById('servidor_cargo_limite');
            select.innerHTML = '<option value="" disabled selected>Selecione um Cargo/Limite...</option>';
            data.forEach(l => {
                select.innerHTML += `<option value="${l.id}" data-req-auth="${l.requer_autorizacao}">${l.cargo} (R$ ${parseFloat(l.valor).toFixed(2).replace('.', ',')})</option>`;
            });
            $(select).select2({
                theme: 'bootstrap-5',
                dropdownParent: $('#modal-servidor')
            }).off('change').on('change', function() {
                const reqAuth = $(this).find(':selected').data('req-auth');
                if (reqAuth === true || reqAuth === 'true') {
                    $('.campos-autorizacao').removeClass('d-none');
                } else {
                    $('.campos-autorizacao').addClass('d-none');
                    // Limpar valores se não for requerido
                    document.getElementById('servidor_protocolo_autorizacao').value = '';
                    document.getElementById('servidor_inicio_validade_autorizacao').value = '';
                }
            });
        }
    } catch(e) { console.error(e); }
}

async function abrirModalNovoServidor() {
    document.getElementById('form-servidor').reset();
    document.getElementById('servidor_id').value = '';
    await popularSelectLimites();
    const modal = new bootstrap.Modal(document.getElementById('modal-servidor'));
    modal.show();
}

async function editarServidor(id) {
    await popularSelectLimites();
    try {
        const res = await fetch(`/reembolsos/api/servidores/${id}/`);
        if(res.ok) {
            const data = await res.json();
            document.getElementById('servidor_id').value = data.id;
            document.getElementById('servidor_nome').value = data.nome;
            document.getElementById('servidor_cpf').value = data.cpf;
            document.getElementById('servidor_ativo').checked = data.ativo;
            
            // Popula os campos antes de acionar a mudança do select (para que não sejam apagados)
            document.getElementById('servidor_protocolo_autorizacao').value = data.protocolo_autorizacao || '';
            document.getElementById('servidor_inicio_validade_autorizacao').value = data.inicio_validade_autorizacao || '';
            
            $('#servidor_cargo_limite').val(data.cargo_limite).trigger('change');
            document.getElementById('servidor_portaria').value = data.portaria_designacao || '';
            document.getElementById('servidor_data_portaria').value = data.data_publicacao_portaria || '';
            document.getElementById('servidor_banco').value = data.banco;
            document.getElementById('servidor_agencia').value = data.agencia;
            document.getElementById('servidor_conta').value = data.conta_corrente;
            document.getElementById('servidor_linha').value = data.telefone_linha;
            document.getElementById('servidor_nota_designacao').value = data.nota_designacao || '';
            document.getElementById('servidor_nota_autorizacao').value = data.nota_autorizacao || '';
            document.getElementById('servidor_observacoes').value = data.observacoes || '';
            
            const modal = new bootstrap.Modal(document.getElementById('modal-servidor'));
            modal.show();
        }
    } catch(e) { console.error(e); }
}

async function salvarServidor() {
    const id = document.getElementById('servidor_id').value;
    const method = id ? 'PUT' : 'POST';
    const url = id ? `/reembolsos/api/servidores/${id}/` : '/reembolsos/api/servidores/';
    
    const payload = {
        nome: document.getElementById('servidor_nome').value,
        cpf: document.getElementById('servidor_cpf').value,
        ativo: document.getElementById('servidor_ativo').checked,
        cargo_limite: document.getElementById('servidor_cargo_limite').value,
        portaria_designacao: document.getElementById('servidor_portaria').value,
        data_publicacao_portaria: document.getElementById('servidor_data_portaria').value || null,
        protocolo_autorizacao: document.getElementById('servidor_protocolo_autorizacao').value || null,
        inicio_validade_autorizacao: document.getElementById('servidor_inicio_validade_autorizacao').value || null,
        banco: document.getElementById('servidor_banco').value,
        agencia: document.getElementById('servidor_agencia').value,
        conta_corrente: document.getElementById('servidor_conta').value,
        telefone_linha: document.getElementById('servidor_linha').value,
        nota_designacao: document.getElementById('servidor_nota_designacao').value,
        nota_autorizacao: document.getElementById('servidor_nota_autorizacao').value,
        observacoes: document.getElementById('servidor_observacoes').value,
    };
    
    try {
        const res = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });
        if(res.ok) {
            $('#modal-servidor').modal('hide');
            $('#tabela-servidores').DataTable().ajax.reload();
            carregarMétricas();
            Swal.fire("Sucesso", "Servidor salvo com sucesso!", "success");
        } else {
            const err = await res.json();
            console.error(err);
            Swal.fire("Erro", "Verifique os dados informados.", "error");
        }
    } catch(e) { console.error(e); }
}

async function excluirServidor(id) {
    if(await confirmDelete()) {
        try {
            const res = await fetch(`/reembolsos/api/servidores/${id}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            if(res.ok) {
                $('#tabela-servidores').DataTable().ajax.reload();
                carregarMétricas();
                Swal.fire("Excluído!", "", "success");
            }
        } catch(e) { console.error(e); }
    }
}

async function imprimirRelatorioAnual(servidorId) {
    const currentYear = new Date().getFullYear();
    const { value: ano } = await Swal.fire({
        title: 'Emitir Relatório Anual',
        text: 'Informe o Ano Base para o relatório:',
        input: 'number',
        inputValue: currentYear,
        showCancelButton: true,
        confirmButtonText: 'Gerar PDF',
        cancelButtonText: 'Cancelar',
        inputValidator: (value) => {
            if (!value || value < 2000 || value > 2100) {
                return 'Por favor, digite um ano válido (ex: 2026)';
            }
        }
    });

    if (ano) {
        window.open(`/reembolsos/relatorio/anual/${servidorId}/?ano=${ano}`, '_blank');
    }
}
// ---------------------- SOLICITACAO ----------------------
async function popularSelectServidores() {
    const res = await fetch('/reembolsos/api/servidores/');
    if(res.ok) {
        const data = await res.json();
        const select = document.getElementById('solicitacao_servidor');
        select.innerHTML = '<option value="" disabled selected>Selecione um Servidor...</option>';
        data.forEach(s => {
            const statusLabel = s.ativo ? '' : ' (Inativo)';
            select.innerHTML += `<option value="${s.id}">${s.nome} (${s.cpf})${statusLabel}</option>`;
        });
        // Select2 opcional
        $(select).select2({
            theme: 'bootstrap-5',
            dropdownParent: $('#modal-solicitacao')
        });
    }
}

function adicionarFatura(data = null) {
    const container = document.getElementById('faturas-container');
    const template = document.getElementById('fatura-template').content.cloneNode(true);
    const item = template.querySelector('.fatura-item');
    
    if (data) {
        item.querySelector('.fatura-inicio').value = data.periodo_inicio || '';
        item.querySelector('.fatura-fim').value = data.periodo_fim || '';
        item.querySelector('.fatura-valor').value = data.valor_fatura ? parseFloat(data.valor_fatura).toFixed(2).replace('.', ',') : '';
        item.querySelector('.fatura-servico').value = data.valor_servico ? parseFloat(data.valor_servico).toFixed(2).replace('.', ',') : '';
        item.querySelector('.fatura-doc').value = data.fatura_anexa || '';
        item.querySelector('.fatura-comprovante').value = data.comprovante_pagamento || '';
        
        const chk = item.querySelector('.fatura-aprovada');
        const justCont = item.querySelector('.fatura-justificativa-container');
        if (data.aprovada === false) {
            chk.checked = false;
            chk.nextElementSibling.classList.remove('text-success');
            chk.nextElementSibling.classList.add('text-danger');
            chk.nextElementSibling.textContent = 'Fatura Negada';
            justCont.style.display = 'block';
            item.querySelector('.fatura-justificativa').value = data.justificativa_negacao || '';
        }
    }
    
    // Event Listener for the Aprovada Checkbox
    const aprovadaCheckbox = item.querySelector('.fatura-aprovada');
    const justContainer = item.querySelector('.fatura-justificativa-container');
    const lbl = aprovadaCheckbox.nextElementSibling;
    aprovadaCheckbox.addEventListener('change', function() {
        if (this.checked) {
            lbl.classList.remove('text-danger');
            lbl.classList.add('text-success');
            lbl.textContent = 'Fatura Aprovada';
            justContainer.style.display = 'none';
            item.querySelector('.fatura-justificativa').value = '';
        } else {
            lbl.classList.remove('text-success');
            lbl.classList.add('text-danger');
            lbl.textContent = 'Fatura Negada';
            justContainer.style.display = 'block';
        }
    });
    
    // Configura os masks para essa nova fatura
    const valorFields = item.querySelectorAll('.mask-moeda');
    valorFields.forEach(el => {
        IMask(el, {
            mask: 'R$ num',
            blocks: {
                num: {
                    mask: Number,
                    scale: 2,
                    thousandsSeparator: '.',
                    padFractionalZeros: true,
                    normalizeZeros: true,
                    radix: ',',
                    mapToRadix: ['.']
                }
            }
        });
    });

    item.querySelector('.btn-remove-fatura').addEventListener('click', function() {
        item.remove();
    });

    container.appendChild(item);
}

document.getElementById('btn-add-fatura').addEventListener('click', () => adicionarFatura());

function adicionarObservacao(texto = '') {
    const container = document.getElementById('observacoes-container');
    const template = document.getElementById('observacao-template').content.cloneNode(true);
    const item = template.querySelector('.observacao-item');
    
    item.querySelector('.solicitacao-obs-input').value = texto;
    item.querySelector('.btn-remove-obs').addEventListener('click', function() {
        item.remove();
    });
    
    container.appendChild(item);
}

document.getElementById('btn-add-obs').addEventListener('click', () => adicionarObservacao());

async function abrirModalNovaSolicitacao() {
    document.getElementById('form-solicitacao').reset();
    document.getElementById('solicitacao_id').value = '';
    document.getElementById('faturas-container').innerHTML = '';
    document.getElementById('observacoes-container').innerHTML = '';
    document.getElementById('modal-solicitacao-titulo').innerHTML = '<i class="bi bi-file-earmark-plus me-2"></i>Nova Solicitação de Reembolso';
    adicionarFatura(); // Começa com 1 fatura vazia
    await popularSelectServidores();
    const modal = new bootstrap.Modal(document.getElementById('modal-solicitacao'));
    modal.show();
}

async function editarSolicitacao(id, concluir = false) {
    try {
        const res = await fetch(`/reembolsos/api/solicitacoes/${id}/`);
        if(res.ok) {
            const data = await res.json();
            document.getElementById('form-solicitacao').reset();
            document.getElementById('faturas-container').innerHTML = '';
            document.getElementById('observacoes-container').innerHTML = '';
            
            document.getElementById('solicitacao_id').value = data.id;
            await popularSelectServidores();
            $('#solicitacao_servidor').val(data.servidor).trigger('change');
            
            document.getElementById('solicitacao_protocolo_sei').value = data.protocolo_sei || '';
            document.getElementById('solicitacao_ordem_bancaria').value = data.protocolo_ordem_bancaria || '';
            document.getElementById('solicitacao_data_pagamento').value = data.data_pagamento || '';

            // Se vier do botão Concluir, forçar status concluido e atualizar título
            if (concluir) {
                document.getElementById('solicitacao_status').value = 'concluido';
                document.getElementById('modal-solicitacao-titulo').innerHTML = '<i class="bi bi-check-circle-fill me-2 text-success"></i>Concluir Solicitação de Reembolso';
            } else {
                document.getElementById('solicitacao_status').value = data.status;
                document.getElementById('modal-solicitacao-titulo').innerHTML = '<i class="bi bi-pencil-square me-2 text-primary"></i>Editar Solicitação de Reembolso';
            }
            
            if (data.observacoes) {
                const obsArray = data.observacoes.split('|||');
                obsArray.forEach(txt => {
                    if(txt.trim()) adicionarObservacao(txt.trim());
                });
            }
            
            if (data.faturas && data.faturas.length > 0) {
                data.faturas.forEach(f => adicionarFatura(f));
            } else {
                adicionarFatura();
            }
            
            const modal = new bootstrap.Modal(document.getElementById('modal-solicitacao'));
            modal.show();

            // Se "Concluir", scroll para a seção de pagamento para facilitar o preenchimento
            if (concluir) {
                setTimeout(() => {
                    const pagSection = document.getElementById('solicitacao_ordem_bancaria');
                    if (pagSection) pagSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    pagSection.focus();
                }, 500);
            }
        }
    } catch(e) { console.error(e); }
}

async function salvarSolicitacao() {
    const id = document.getElementById('solicitacao_id').value;
    const method = id ? 'PUT' : 'POST';
    const url = id ? `/reembolsos/api/solicitacoes/${id}/` : '/reembolsos/api/solicitacoes/';
    
    const faturas = [];
    document.querySelectorAll('#faturas-container .fatura-item').forEach(item => {
        const isAprovada = item.querySelector('.fatura-aprovada').checked;
        const justificativa = isAprovada ? '' : item.querySelector('.fatura-justificativa').value;
        
        faturas.push({
            periodo_inicio: item.querySelector('.fatura-inicio').value,
            periodo_fim: item.querySelector('.fatura-fim').value,
            valor_fatura: item.querySelector('.fatura-valor').value,
            valor_servico: item.querySelector('.fatura-servico').value,
            fatura_anexa: item.querySelector('.fatura-doc').value,
            comprovante_pagamento: item.querySelector('.fatura-comprovante').value,
            aprovada: isAprovada,
            justificativa_negacao: justificativa
        });
    });

    // Validar justificativa
    let errorJustificativa = false;
    faturas.forEach(f => {
        if (!f.aprovada && (!f.justificativa_negacao || f.justificativa_negacao.trim() === '')) {
            errorJustificativa = true;
        }
    });

    if (errorJustificativa) {
        Swal.fire("Atenção", "Preencha a justificativa para todas as faturas negadas.", "warning");
        return;
    }

    const obsInputs = document.querySelectorAll('.solicitacao-obs-input');
    const observacoesArray = [];
    obsInputs.forEach(input => {
        if (input.value.trim()) observacoesArray.push(input.value.trim());
    });
    const observacoesJoined = observacoesArray.join('|||');

    const payload = {
        servidor: document.getElementById('solicitacao_servidor').value,
        protocolo_sei: document.getElementById('solicitacao_protocolo_sei').value,
        protocolo_ordem_bancaria: document.getElementById('solicitacao_ordem_bancaria').value,
        data_pagamento: document.getElementById('solicitacao_data_pagamento').value || null,
        status: document.getElementById('solicitacao_status').value,
        observacoes: observacoesJoined,
        faturas: faturas
    };
    
    if(!payload.servidor) { Swal.fire("Atenção", "Selecione o servidor", "warning"); return; }
    
    try {
        const res = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });
        if(res.ok) {
            // Fecha o modal de solicitação
            const modalEl = document.getElementById('modal-solicitacao');
            bootstrap.Modal.getInstance(modalEl)?.hide();

            // Recarrega a tabela de solicitações
            if ($.fn.DataTable.isDataTable('#tabela-solicitacoes')) {
                $('#tabela-solicitacoes').DataTable().ajax.reload(null, false);
            }

            // Atualiza métricas e o widget de pendências
            carregarMétricas();
            carregarWidgetPendencias();

            Swal.fire({
                icon: 'success',
                title: 'Sucesso!',
                text: 'Solicitação salva com sucesso!',
                timer: 2000,
                showConfirmButton: false
            });
        } else {
            const err = await res.json();
            console.error(err);
            Swal.fire("Erro", "Verifique os dados informados.", "error");
        }
    } catch(e) { console.error(e); }
}

async function excluirSolicitacao(id) {
    if(await confirmDelete()) {
        try {
            const res = await fetch(`/reembolsos/api/solicitacoes/${id}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            if(res.ok) {
                $('#tabela-solicitacoes').DataTable().ajax.reload();
                carregarMétricas();
                Swal.fire("Excluído!", "", "success");
            }
        } catch(e) { console.error(e); }
    }
}

async function imprimirRelatorioSolicitacao(id) {
    try {
        const res = await fetch(`/reembolsos/api/solicitacoes/${id}/`);
        if(res.ok) {
            const data = await res.json();
            if (data.faturas && data.faturas.length > 0) {
                const anos = new Set();
                data.faturas.forEach(f => {
                    // Extract year from YYYY-MM-DD
                    if (f.periodo_fim) {
                        const year = f.periodo_fim.split('-')[0];
                        if (year) anos.add(parseInt(year));
                    }
                });
                
                const anosArray = Array.from(anos).sort();
                
                if (anosArray.length > 1) {
                    let optionsHtml = '';
                    anosArray.forEach(ano => {
                        optionsHtml += `<button class="btn btn-primary m-2" onclick="window.open('/reembolsos/relatorio/solicitacao/${id}/?ano=${ano}', '_blank'); Swal.close();">${ano}</button>`;
                    });
                    
                    Swal.fire({
                        title: 'Múltiplos Anos Detectados',
                        html: `Esta solicitação possui faturas de múltiplos anos.<br>Qual relatório de competência deseja gerar?<br><br>${optionsHtml}`,
                        showConfirmButton: false,
                        showCancelButton: true,
                        cancelButtonText: 'Cancelar'
                    });
                } else {
                    let anoParam = anosArray.length === 1 ? `?ano=${anosArray[0]}` : '';
                    window.open(`/reembolsos/relatorio/solicitacao/${id}/${anoParam}`, '_blank');
                }
            } else {
                window.open(`/reembolsos/relatorio/solicitacao/${id}/`, '_blank');
            }
        } else {
            window.open(`/reembolsos/relatorio/solicitacao/${id}/`, '_blank');
        }
    } catch(e) { 
        console.error(e);
        window.open(`/reembolsos/relatorio/solicitacao/${id}/`, '_blank');
    }
}

// Helpers
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

function confirmDelete() {
    return Swal.fire({
        title: 'Você tem certeza?',
        text: "Essa ação não pode ser desfeita!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        return result.isConfirmed;
    });
}
