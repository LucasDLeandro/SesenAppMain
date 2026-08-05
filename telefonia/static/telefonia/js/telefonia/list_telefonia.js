document.addEventListener("DOMContentLoaded", function() {
    
    // Configurações Globais do DataTables (Tradução)
    const dtLanguage = {
        "sEmptyTable": "Nenhum registro encontrado",
        "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros",
        "sInfoEmpty": "Mostrando 0 até 0 de 0 registros",
        "sInfoFiltered": "(Filtrados de _MAX_ registros)",
        "sInfoPostFix": "",
        "sInfoThousands": ".",
        "sLengthMenu": "_MENU_ resultados por página",
        "sLoadingRecords": "Carregando...",
        "sProcessing": "Processando...",
        "sZeroRecords": "Nenhum registro encontrado",
        "sSearch": "Pesquisar",
        "oPaginate": {
            "sNext": "Próximo",
            "sPrevious": "Anterior",
            "sFirst": "Primeiro",
            "sLast": "Último"
        },
        "oAria": {
            "sSortAscending": ": Ordenar colunas de forma ascendente",
            "sSortDescending": ": Ordenar colunas de forma descendente"
        }
    };

    // Função utilitária para aplicar filtros de pesquisa individual por coluna
    function aplicarFiltroColunas(tabela) {
        var thead = $(tabela.table().header());
        // Evitar duplicação da linha de filtros
        if (thead.find('.filtro-coluna-row').length) return;

        var tr = $('<tr class="filtro-coluna-row"></tr>');

        tabela.columns().every(function(index) {
            var column = this;
            var headerText = $(column.header()).text().trim();
            var th = $('<th style="padding: 6px 4px;"></th>');

            // Não adicionar filtro em colunas de Ações
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
                    'background-color': '#f8f9fa',
                    'font-weight': 'normal'
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

            // Impedir que o clique no input dispare ordenação
            input.on('click keypress keydown', function(e) { e.stopPropagation(); });

            th.append(input).appendTo(tr);
        });

        thead.append(tr);
    }


    // 1. Tabela de Solicitações de Aparelhos
    $('#tabela-solicitacoes').DataTable({
        responsive: true,
        order: [[0, 'desc']],
        ajax: {
            url: '/telefonia/api/solicitacoes/',
            dataSrc: '' // Como o ViewSet DRF padrão retorna lista se não houver paginação explícita
        },
        columns: [
            { 
                data: 'data',
                render: function(data, type, row) {
                    if(!data) return '';
                    if (type === 'sort' || type === 'type') return data;
                    let d = new Date(data);
                    return d.toLocaleDateString('pt-BR') + ' ' + d.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
                }
            },
            { data: 'protocolo' },
            { 
                data: 'unidade',
                render: function(data) {
                    if(!data) return '-';
                    return data.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                }
            },
            { 
                data: 'sigla_unidade',
                defaultContent: '-',
                render: function(data) {
                    if(!data) return '-';
                    return data.toUpperCase();
                }
            },
            { 
                data: 'local',
                defaultContent: '-'
            },
            { data: 'qnt_solicitada' },
            { 
                data: 'status',
                render: function(data) {
                    let fs = 'font-size: 13px; padding: 6px 10px;';
                    if(data === 'recebida') return `<span class="badge" style="background-color: #fd7e14; color: white; ${fs}">Recebida</span>`;
                    if(data === 'em_analise') return `<span class="badge bg-warning text-dark" style="${fs}">Em Análise</span>`;
                    if(data === 'pendente') return `<span class="badge bg-danger" style="${fs}">Pendente</span>`;
                    if(data === 'concluida') return `<span class="badge bg-success" style="${fs}">Concluída</span>`;
                    if(data === 'aguardando_supervisor_aparelho') return `<span class="badge bg-info text-dark" style="${fs}">Apenas Finalizar</span>`;
                    return data;
                }
            },
            {
                data: null,
                orderable: false,
                render: function(data, type, row) {
                    let buttons = `<button class="btn btn-sm btn-outline-info me-1" onclick="visualizarSolicitacao(${row.id})" title="Visualizar Solicitação">
                                <i class="bi bi-eye-fill"></i>
                            </button>`;
                    if (window.userCanEdit) {
                        buttons += `<button class="btn btn-sm btn-outline-primary me-1" onclick="abrirEdicaoSolicitacao(${row.id})" title="Editar Solicitação">
                                <i class="bi bi-pencil-square"></i>
                            </button>`;
                        buttons += `<button class="btn btn-sm btn-outline-danger" onclick="deletarSolicitacao(${row.id})" title="Deletar Solicitação">
                                <i class="bi bi-trash"></i>
                            </button>`;
                    }
                    return buttons;
                }
            }
        ],
        language: dtLanguage,
        responsive: true,
        orderCellsTop: true,
        initComplete: function() {
            aplicarFiltroColunas(this.api());
        }
    });

    // 2. Tabela de Solicitações de Senhas
    $('#tabela-senhas').DataTable({
        responsive: true,
        order: [[0, 'desc']],
        ajax: {
            url: '/telefonia/api/senhas/',
            dataSrc: ''
        },
        columns: [
            { 
                data: 'created_at',
                render: function(data, type, row) {
                    if(!data) return '';
                    if (type === 'sort' || type === 'type') return data;
                    let d = new Date(data);
                    return d.toLocaleDateString('pt-BR') + ' ' + d.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
                }
            },
            { data: 'protocolo' },
            { data: 'usuario' },
            { 
                data: 'sigla_unidade',
                defaultContent: '-',
                render: function(data) {
                    if(!data) return '-';
                    return data.toUpperCase();
                }
            },
            { data: 'ramal' },
            { 
                data: 'desvio',
                render: function(data) {
                    return data ? '<span class="text-success fw-bold">Sim</span>' : '<span class="text-secondary">Não</span>';
                }
            },
            { 
                data: 'status',
                render: function(data) {
                    if(data === 'recebida') return '<span class="badge bg-primary">Recebida</span>';
                    if(data === 'aguardando_supervisor') return '<span class="badge bg-warning text-dark">Aguardando Sup.</span>';
                    if(data === 'finalizada') return '<span class="badge bg-success">Finalizada</span>';
                    return '<span class="badge bg-secondary">Recebida</span>'; // default retroativo
                }
            },
            {
                data: 'id',
                orderable: false,
                className: 'text-end',
                render: function(data, type, row) {
                    let buttons = `
                        <div class="d-flex justify-content-end gap-2">
                            <button class="btn btn-sm btn-outline-info shadow-sm" onclick="visualizarSenha(${data})" title="Visualizar Detalhes">
                                <i class="bi bi-eye"></i>
                            </button>
                    `;

                    // Botão para o Técnico
                    if (!row.status || row.status === 'recebida') {
                        buttons += `
                            <button class="btn btn-sm btn-success shadow-sm" onclick="abrirModalConcluirSenha(${data})" title="Gerar Senha (Técnico)">
                                <i class="bi bi-check-circle"></i> Concluir
                            </button>
                        `;
                    }
                    
                    // Botão para o Supervisor
                    if (row.status === 'aguardando_supervisor' || row.status === 'finalizada') {
                        if (row.status === 'finalizada') {
                            buttons += `
                                <button class="btn btn-sm btn-warning text-dark shadow-sm" onclick="abrirModalFinalizarSenha(${data}, '${row.status}')" title="Reenviar E-mail">
                                    <i class="bi bi-send-check"></i>
                                </button>
                            `;
                        } else {
                            buttons += `
                                <button class="btn btn-sm btn-warning text-dark shadow-sm" onclick="abrirModalFinalizarSenha(${data}, '${row.status}')" title="Finalizar e Enviar E-mail (Supervisor)">
                                    <i class="bi bi-envelope-check"></i> Finalizar
                                </button>
                            `;
                        }
                    }

                    // Botões de utilidade extra após concluído
                    if (row.status === 'finalizada' || row.status === 'aguardando_supervisor') {
                        buttons += `
                            <a href="/telefonia/senha/${data}/pdf/" target="_blank" class="btn btn-sm btn-outline-danger shadow-sm" title="Imprimir Termo">
                                <i class="bi bi-file-earmark-pdf"></i>
                            </a>
                        `;
                    }

                    buttons += `</div>`;
                    return buttons;
                }
            }
        ],
        language: dtLanguage,
        responsive: true,
        orderCellsTop: true,
        initComplete: function() {
            aplicarFiltroColunas(this.api());
        }
    });

    // 3. Tabela de Aparelhos VOIP (Geral)
    $('#tabela-aparelhos').DataTable({
        responsive: true,
        order: [[0, 'desc']],
        ajax: {
            url: '/gestao_patrimonio/api/aparelhos-telefonicos/',
            dataSrc: ''
        },
        columns: [
            { 
                data: 'created_at',
                render: function(data, type, row) {
                    if(!data) return '';
                    if (type === 'sort' || type === 'type') return data;
                    let d = new Date(data);
                    return d.toLocaleDateString('pt-BR');
                }
            },
            { data: 'patrimonio' },
            { data: 'modelo' },
            { data: 'mac_address' },
            { data: 'ramal' },
            { 
                data: 'integridade',
                render: function(data) {
                    if(data === 'funciona') return '<span class="badge bg-success">Funciona</span>';
                    if(data === 'defeito') return '<span class="badge bg-danger">Defeito</span>';
                    return data;
                }
            },
            {
                data: 'id',
                orderable: false,
                render: function(data) {
                    let buttons = `<button class="btn btn-sm btn-outline-info me-1" onclick="visualizarAparelho(${data})" title="Visualizar Detalhes">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="editarAparelho(${data})" title="Editar Aparelho">
                                <i class="bi bi-pencil-square"></i>
                            </button>`;
                    if (window.userCanEdit) {
                        buttons += `<button class="btn btn-sm btn-outline-danger" onclick="deletarAparelho(${data})" title="Deletar Aparelho">
                                <i class="bi bi-trash"></i>
                            </button>`;
                    }
                    return buttons;
                }
            }
        ],
        language: dtLanguage,
        responsive: true,
        orderCellsTop: true,
        initComplete: function() {
            aplicarFiltroColunas(this.api());
        }
    });

    // Limpa o formulário de Aparelhos VOIP ao fechar, para evitar misturar Novo Cadastro com Edição
    document.getElementById('modal-aparelho-voip').addEventListener('hidden.bs.modal', function () {
        document.getElementById('form-aparelho-voip').reset();
        document.getElementById('id_oculto_aparelho').value = '';
    });

    // 4. Tabela de Remessas para Manutenção
    $('#tabela-remessas').DataTable({
        responsive: true,
        order: [[0, 'desc']],
        ajax: {
            url: '/telefonia/api/remessas/',
            dataSrc: ''
        },
        columns: [
            { 
                data: 'data_remessa',
                render: function(data, type, row) {
                    if(!data) return '-';
                    if (type === 'sort' || type === 'type') return data;
                    let d = new Date(data);
                    return d.toLocaleDateString('pt-BR');
                }
            },
            { data: 'memorando', defaultContent: '-' },
            { data: 'empresa_contratada', defaultContent: '-' },
            { 
                data: 'aparelhos_detalhes',
                render: function(data) {
                    return data ? data.length : 0;
                }
            },
            {
                data: 'id',
                orderable: false,
                render: function(data) {
                    return `<button class="btn btn-sm btn-outline-danger me-1" onclick="window.open('/telefonia/remessa/${data}/pdf/', '_blank')" title="Baixar PDF">
                                <i class="bi bi-file-earmark-pdf-fill"></i> PDF
                            </button>`;
                }
            }
        ],
        language: dtLanguage,
        responsive: true,
        orderCellsTop: true,
        initComplete: function() {
            aplicarFiltroColunas(this.api());
        }
    });

    // 5. Tabela do Modal de Solicitações Recebidas
    $('#tabela-recebidas-modal').DataTable({
        responsive: true,
        order: [[0, 'desc']],
        ajax: function (data, callback, settings) {
            Promise.all([
                fetch('/telefonia/api/solicitacoes/'),
                fetch('/telefonia/api/senhas/'),
                fetch('/telefonia/api/eventos/')
            ]).then(async ([resSol, resSenhas, resEventos]) => {
                let pendentes = [];
                if (resSol.ok) {
                    const solicitacoes = await resSol.json();
                    const pendSol = solicitacoes.filter(s => s.status === 'recebida' || s.status === 'pendente' || s.status === 'em_analise' || s.status === 'aguardando_supervisor_aparelho');
                    pendSol.forEach(s => {
                        s.tipo_demanda = 'Aparelho';
                        s.data_comparacao = new Date(s.data).getTime();
                    });
                    pendentes = pendentes.concat(pendSol);
                }
                if (resSenhas.ok) {
                    const senhas = await resSenhas.json();
                    const pendSenhas = senhas.filter(s => s.status === 'recebida' || s.status === 'aguardando_supervisor');
                    pendSenhas.forEach(s => {
                        s.tipo_demanda = 'Senha';
                        s.data_comparacao = new Date(s.created_at).getTime();
                        s.local = s.usuario; // unifica a propriedade para a coluna
                    });
                    pendentes = pendentes.concat(pendSenhas);
                }
                if (resEventos.ok) {
                    const eventos = await resEventos.json();
                    const pendEventos = eventos.filter(s => s.status === 'em_andamento');
                    pendEventos.forEach(s => {
                        s.tipo_demanda = 'Evento';
                        s.protocolo = s.evento_nome;
                        s.unidade = s.solicitante;
                        s.sigla_unidade = '-';
                        s.data_comparacao = new Date(s.data_inicio).getTime();
                    });
                    pendentes = pendentes.concat(pendEventos);
                }
                callback({ data: pendentes });
            });
        },
        columns: [
            { 
                data: 'data_comparacao',
                className: 'text-nowrap align-middle',
                render: function(data, type, row) {
                    if(!data) return '';
                    if (type === 'sort' || type === 'type') return data;
                    let d = new Date(data);
                    return d.toLocaleDateString('pt-BR');
                }
            },
            { 
                data: 'protocolo',
                className: 'text-nowrap align-middle'
            },
            { 
                data: 'tipo_demanda',
                className: 'text-nowrap align-middle text-center',
                render: function(data) {
                    if (data === 'Aparelho') return `<span class="badge bg-secondary"><i class="bi bi-telephone"></i> Aparelho</span>`;
                    if (data === 'Evento') return `<span class="badge bg-primary"><i class="bi bi-calendar-event"></i> Evento</span>`;
                    return `<span class="badge bg-dark"><i class="bi bi-key"></i> Senha</span>`;
                }
            },
            { 
                data: 'unidade',
                className: 'align-middle',
                render: function(data) {
                    if(!data) return '-';
                    return data.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                }
            },
            { 
                data: 'sigla_unidade',
                defaultContent: '-',
                className: 'text-nowrap text-center align-middle',
                render: function(data) {
                    if(!data) return '-';
                    return data.toUpperCase();
                }
            },
            { 
                data: 'local', 
                defaultContent: '-',
                className: 'text-nowrap align-middle text-center'
            },
            { 
                data: 'status',
                className: 'align-middle text-center',
                render: function(data) {
                    let fs = 'font-size: 13px; padding: 6px 10px;';
                    if(data === 'recebida') return `<span class="badge" style="background-color: #fd7e14; color: white; ${fs}">Recebida</span>`;
                    if(data === 'em_analise') return `<span class="badge bg-warning text-dark" style="${fs}">Em Análise</span>`;
                    if(data === 'pendente') return `<span class="badge bg-danger" style="${fs}">Pendente</span>`;
                    if(data === 'aguardando_supervisor') return `<span class="badge bg-info text-dark" style="${fs}">Aguardando Supervisor</span>`;
                    if(data === 'aguardando_supervisor_aparelho') return `<span class="badge bg-info text-dark" style="${fs}">Apenas Finalizar</span>`;
                    return data;
                }
            },
            {
                data: null,
                orderable: false,
                className: 'text-nowrap align-middle text-end',
                render: function(data, type, row) {
                    if (row.tipo_demanda === 'Aparelho') {
                        if (row.status === 'aguardando_supervisor_aparelho') {
                            return `<div class="d-flex justify-content-end gap-1">
                                        <button class="btn btn-sm btn-outline-warning text-dark text-nowrap" style="white-space: nowrap;" onclick="abrirModalFinalizarAdministrativo(${row.id})" title="Finalizar Administrativamente">
                                            <i class="bi bi-file-earmark-check me-1"></i> Anexar Termo
                                        </button>
                                    </div>`;
                        } else {
                            return `<div class="d-flex justify-content-end gap-1">
                                        <button class="btn btn-sm btn-outline-success text-nowrap" style="white-space: nowrap;" onclick="abrirConclusao(${row.id})" title="Concluir Instalação">
                                            <i class="bi bi-check2-circle me-1"></i> Concluir
                                        </button>
                                        <button class="btn btn-sm btn-outline-info text-nowrap" style="white-space: nowrap;" onclick="visualizarSolicitacao(${row.id})" title="Visualizar Solicitação">
                                            <i class="bi bi-eye-fill"></i>
                                        </button>
                                    </div>`;
                        }
                    } else if (row.tipo_demanda === 'Evento') {
                        return `<div class="d-flex justify-content-end gap-1">
                                    <button class="btn btn-sm btn-outline-primary text-nowrap" style="white-space: nowrap;" onclick="abrirModalEvento(${row.id})" title="Ver / Recolher Evento">
                                        <i class="bi bi-eye"></i> Detalhes / Recolher
                                    </button>
                                </div>`;
                    } else {
                        if (row.status === 'aguardando_supervisor') {
                            return `<div class="d-flex justify-content-end gap-1">
                                        <button class="btn btn-sm btn-outline-warning text-dark text-nowrap" style="white-space: nowrap;" onclick="abrirModalFinalizarSenha(${row.id}, '${row.status}')" title="Finalizar e Enviar E-mail">
                                            <i class="bi bi-envelope-check me-1"></i> Enviar E-mail
                                        </button>
                                    </div>`;
                        } else {
                            return `<div class="d-flex justify-content-end gap-1">
                                        <button class="btn btn-sm btn-outline-success text-nowrap" style="white-space: nowrap;" onclick="abrirModalConcluirSenha(${row.id})" title="Concluir Geração de Senha">
                                            <i class="bi bi-gear me-1"></i> Gerar Senha
                                        </button>
                                    </div>`;
                        }
                    }
                }
            }
        ],
        language: dtLanguage,
        responsive: true,
        orderCellsTop: true,
        order: [[0, 'desc']],
        initComplete: function() {
            aplicarFiltroColunas(this.api());
        }
    });

    // Carregar Widget de Recebidas na Dashboard
    carregarWidgetRecebidas();

});

// Função disparada pelo botão Editar na tabela
window.editarAparelho = async function(id) {
    try {
        const resposta = await fetch(`/gestao_patrimonio/api/aparelhos-telefonicos/${id}/`);
        if (resposta.ok) {
            const aparelho = await resposta.json();
            
            // Preenche os campos do formulário
            document.getElementById('id_oculto_aparelho').value = aparelho.id;
            const container = document.getElementById('aparelhos-container');
            const row = container.querySelector('.aparelho-row');
            
            row.querySelector('.input-patrimonio').value = aparelho.patrimonio || '';
            row.querySelector('.input-modelo').value = aparelho.modelo || '';
            if(row.querySelector('.input-funcao')) {
                row.querySelector('.input-funcao').value = aparelho.funcao_aparelho || 'fixo';
            }
            row.querySelector('.input-fcn').value = aparelho.fcn || '';
            row.querySelector('.input-mac').value = aparelho.mac_address || '';
            
            if (aparelho.integridade) {
                row.querySelector('.input-integridade').value = aparelho.integridade;
            }
            
            // Exibe o modal
            // Utilizando o bootstrap via global scope
            const modalEl = document.getElementById('modal-aparelho-voip');
            const modalInstance = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            modalInstance.show();
            
        } else {
            Swal.fire("Erro!", "Não foi possível carregar os dados do aparelho.", "error");
        }
    } catch (erro) {
        console.error(erro);
        Swal.fire("Erro!", "Problema de conexão ao tentar buscar o aparelho.", "error");
    }
};

// Função para abrir modal de conclusão de solicitação e preencher dados
window.abrirConclusao = async function(id) {
    try {
        const resposta = await fetch(`/telefonia/api/solicitacoes/${id}/`);
        if (resposta.ok) {
            const dados = await resposta.json();
            document.getElementById('id_conclusao_solicitacao').value = dados.id;
            document.getElementById('local_base_solicitacao').value = dados.local || '';
            document.getElementById('tecnico_responsavel_conclusao').value = dados.tecnico_responsavel || '';
            document.getElementById('relatorio_conclusao').value = dados.relatorio || '';
            
            // Dispara evento manual para o modal carregar os aparelhos
            const modalEl = document.getElementById('modal-concluir-solicitacao');
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        } else {
            Swal.fire("Erro!", "Erro ao buscar dados da solicitação.", "error");
        }
    } catch (erro) {
        console.error("Erro:", erro);
        Swal.fire("Erro!", "Não foi possível carregar a solicitação. Tente novamente.", "error");
    }
}

// Função disparada pelo botão Editar Defeito na tabela
window.editarDefeito = async function(id) {
    try {
        const resposta = await fetch(`/telefonia/api/defeitos/${id}/`);
        if (resposta.ok) {
            const defeito = await resposta.json();
            
            document.getElementById('id_oculto_defeito').value = defeito.id;
            
            // Salva o aparelho selecionado para restaurar após o fetch do select
            if (defeito.aparelho) {
                document.getElementById('aparelho').setAttribute('data-selected-value', defeito.aparelho);
            }
            
            // Tratamento das datas para o input type="datetime-local" (YYYY-MM-DDTHH:mm)
            const formataData = (dataStr) => {
                if(!dataStr) return '';
                const d = new Date(dataStr);
                d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
                return d.toISOString().slice(0,16);
            };
            
            document.getElementById('data_defeito').value = formataData(defeito.data_defeito);
            document.getElementById('defeito').value = defeito.defeito || '';
            document.getElementById('data_retirada_plaqueta').value = formataData(defeito.data_retirada_plaqueta);
            document.getElementById('memo_solicitacao_baixa').value = formataData(defeito.memo_solicitacao_baixa);
            document.getElementById('data_baixa_patrimonio').value = formataData(defeito.data_baixa_patrimonio);
            document.getElementById('data_saida_manutencao').value = formataData(defeito.data_saida_manutencao);
            
            const modalEl = document.getElementById('modal-aparelho-defeito');
            const modalInstance = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            modalInstance.show();
            
        } else {
            Swal.fire("Erro!", "Não foi possível carregar os dados do defeito.", "error");
        }
    } catch (erro) {
        console.error(erro);
        Swal.fire("Erro!", "Problema de conexão ao tentar buscar o defeito.", "error");
    }
};

// ==========================================
// NOVAS FUNÇÕES: DASHBOARD E VISUALIZAÇÃO
// ==========================================

// Função para carregar mini lista na Dashboard
window.carregarWidgetRecebidas = async function() {
    try {
        const [resSol, resSenhas, resEventos] = await Promise.all([
            fetch('/telefonia/api/solicitacoes/'),
            fetch('/telefonia/api/senhas/'),
            fetch('/telefonia/api/eventos/')
        ]);
        
        let pendentes = [];

        if (resSol.ok) {
            const solicitacoes = await resSol.json();
            const pendSol = solicitacoes.filter(s => s.status === 'recebida' || s.status === 'pendente' || s.status === 'em_analise' || s.status === 'aguardando_supervisor_aparelho');
            pendSol.forEach(s => {
                s.tipo_demanda = 'Aparelho';
                s.data_comparacao = new Date(s.data).getTime();
            });
            pendentes = pendentes.concat(pendSol);
        }

        if (resSenhas.ok) {
            const senhas = await resSenhas.json();
            const pendSenhas = senhas.filter(s => s.status === 'recebida' || s.status === 'aguardando_supervisor');
            pendSenhas.forEach(s => {
                s.tipo_demanda = 'Senha';
                s.data_comparacao = new Date(s.created_at).getTime();
            });
            pendentes = pendentes.concat(pendSenhas);
        }
if (resEventos.ok) {
            const eventos = await resEventos.json();
            const pendEventos = eventos.filter(s => s.status === 'em_andamento');
            pendEventos.forEach(s => {
                s.tipo_demanda = 'Evento';
                s.protocolo = s.evento_nome;
                s.sigla_unidade = '-';
                s.data_comparacao = new Date(s.data_inicio).getTime();
            });
            pendentes = pendentes.concat(pendEventos);
        }

        // Ordena pela data mais recente primeiro
        pendentes.sort((a, b) => b.data_comparacao - a.data_comparacao);
        
        document.getElementById('badge-recebidas-count').textContent = pendentes.length;
        const listGroup = document.getElementById('lista-recebidas-dashboard');
        listGroup.innerHTML = ''; // limpa
        
        if (pendentes.length === 0) {
            listGroup.innerHTML = '<div class="text-center text-muted py-2"><i class="bi bi-emoji-smile me-2"></i>Nenhuma solicitação pendente! Tudo em dia.</div>';
            // Remove estilos de alerta
            document.getElementById('card-widget-recebidas').className = 'card shadow-sm border-0 interactive-card';
            document.getElementById('card-widget-recebidas').style.border = '1px solid #e0e0e0';
            document.getElementById('titulo-widget-recebidas').className = 'fw-bold mb-0 text-success';
            document.getElementById('titulo-widget-recebidas').innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>Status: Tudo em Dia';
            document.getElementById('badge-recebidas-count').className = 'badge bg-success rounded-pill shadow-sm';
            document.getElementById('rodape-widget-recebidas').style.display = 'none';
            return;
        }
        
        // Estilos de alerta
        document.getElementById('rodape-widget-recebidas').style.display = 'block';
        document.getElementById('card-widget-recebidas').className = 'card shadow-sm border-0 interactive-card border-danger border-2 bg-danger-subtle';
        document.getElementById('titulo-widget-recebidas').className = 'fw-bold mb-0 text-danger';
        document.getElementById('titulo-widget-recebidas').innerHTML = '<i class="bi bi-exclamation-triangle-fill me-2"></i>Atenção: Demandas Pendentes';
        document.getElementById('badge-recebidas-count').className = 'badge bg-danger rounded-pill shadow-sm';

        // Exibe as 3 mais recentes no widget
        const max = Math.min(pendentes.length, 3);
        for (let i = 0; i < max; i++) {
            const s = pendentes[i];
            let d = new Date(s.data_comparacao);
            const dataFormatada = d.toLocaleDateString('pt-BR');
            const sigla = s.sigla_unidade ? s.sigla_unidade.toUpperCase() : '-';
            
            listGroup.innerHTML += `
                <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2 mb-1 rounded" style="background-color: #fff5f5; border: 1px solid #ffcaca;">
                    <div>
                        <small class="text-danger d-block mb-0 fw-bold" style="font-size: 0.8rem;"><i class="bi bi-clock-history"></i> Data: ${dataFormatada}</small>
                        <span class="fw-bold text-dark">${s.protocolo}</span> <span class="badge bg-secondary ms-1" style="font-size: 0.7rem;">${s.tipo_demanda}</span>
                        <br><span class="text-muted" style="font-size: 0.85rem;">Unidade: ${sigla}</span>
                    </div>
                    <i class="bi bi-chevron-right text-danger fw-bold fs-5"></i>
                </div>
            `;
        }
        
    } catch (e) {
        console.error("Erro ao carregar widget:", e);
        document.getElementById('lista-recebidas-dashboard').innerHTML = '<div class="text-center text-danger py-3">Erro ao carregar.</div>';
    }
};

window.abrirListaRecebidas = function() {
    // Recarrega os DataTables
    $('#tabela-recebidas-modal').DataTable().ajax.reload(null, false);
    const modalEl = document.getElementById('modal-lista-concluir-solicitacoes');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
};

window.visualizarSolicitacao = async function(id) {
    try {
        const resposta = await fetch(`/telefonia/api/solicitacoes/${id}/`);
        if (resposta.ok) {
            const dados = await resposta.json();
            
            // Tratamento da data
            const formatDate = (dString) => {
                if(!dString) return '-';
                let d = new Date(dString);
                return d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
            };

            // Preenche o modal de visualização
            document.getElementById('vis-protocolo').textContent = dados.protocolo || '-';
            document.getElementById('vis-data').textContent = formatDate(dados.data);
            document.getElementById('vis-unidade').textContent = dados.unidade || '-';
            document.getElementById('vis-sigla').textContent = dados.sigla_unidade ? dados.sigla_unidade.toUpperCase() : '-';
            document.getElementById('vis-local').textContent = dados.local || '-';
            
            const anexoUrl = dados.pdf_termo || dados.midia;
            
            if (dados.termo_transferencia_interna) {
                document.getElementById('vis-termo').textContent = dados.termo_transferencia_interna;
            } else if (anexoUrl) {
                document.getElementById('vis-termo').textContent = '';
            } else {
                document.getElementById('vis-termo').textContent = '-';
            }
            
            // Compatibilidade para solicitações antigas sem múltiplos anexos, mas com PDF único:
            if (anexoUrl && (!dados.anexos || dados.anexos.length === 0)) {
                dados.anexos = [{ arquivo: anexoUrl, id: 'legacy' }];
            }
            
            const sts = dados.status || '-';
            if (sts === 'aguardando_supervisor_aparelho') {
                document.getElementById('vis-status').innerHTML = `<span class="badge bg-info text-dark">APENAS FINALIZAR</span>`;
            } else {
                document.getElementById('vis-status').innerHTML = `<span class="badge bg-secondary">${sts.toUpperCase()}</span>`;
            }
            
            document.getElementById('vis-quantidade').textContent = dados.qnt_solicitada || '-';
            
            document.getElementById('vis-solicitante').textContent = dados.solicitante || '-';
            document.getElementById('vis-contato').textContent = dados.ramal || '-';
            
            document.getElementById('vis_tecnico_responsavel').textContent = dados.tecnico_responsavel || 'Não informado';
            document.getElementById('vis_data_instalacao').textContent = dados.data_instalacao ? formatDate(dados.data_instalacao) : 'Não informado';
            
            document.getElementById('vis_relatorio').textContent = dados.relatorio || 'Sem observações/relatório.';
            
            document.getElementById('vis-ultima-atualizacao').innerHTML = `<i class="bi bi-info-circle me-1"></i> ${dados.ultima_atualizacao || 'Nenhuma atualização registrada'}`;

            // Aparelhos Vinculados / Equipamentos Instalados Unificados
            const secaoAparelhos = document.getElementById('vis-secao-aparelhos-instalados');
            const tbodyAparelhos = document.getElementById('vis-tbody-aparelhos');
            
            secaoAparelhos.style.display = 'block';
            tbodyAparelhos.innerHTML = '';

            if (dados.aparelhos_detalhes && dados.aparelhos_detalhes.length > 0) {
                let maxLen = Math.max(dados.aparelhos_detalhes.length, (dados.anexos || []).length);
                for(let i = 0; i < maxLen; i++) {
                    let ap = dados.aparelhos_detalhes[i] || {};
                    let anexo = (dados.anexos || [])[i];
                    let anexoHtml = '-';
                    if (anexo) {
                        anexoHtml = `
                            <div class="d-flex justify-content-center gap-1">
                                <a href="${anexo.arquivo}" target="_blank" class="btn btn-sm btn-outline-danger" title="Abrir PDF"><i class="bi bi-file-earmark-pdf"></i></a>
                                ${anexo.id !== 'legacy' ? `<button type="button" class="btn btn-sm btn-outline-danger" onclick="excluirAnexo(${dados.id}, ${anexo.id})" title="Excluir PDF"><i class="bi bi-trash"></i></button>` : ''}
                            </div>
                        `;
                    }
                    
                    tbodyAparelhos.innerHTML += `
                        <tr>
                            <td class="d-flex align-items-center justify-content-center gap-2">
                                <strong>${ap.patrimonio || '-'}</strong>
                                ${ap.patrimonio ? `<button type="button" class="btn btn-sm btn-link text-secondary p-0" onclick="window.copiarPatrimonio('${ap.patrimonio}')" title="Copiar Patrimônio"><i class="bi bi-copy"></i></button>` : ''}
                            </td>
                            <td>${ap.sala || '-'}</td>
                            <td>${ap.ramal || '-'}</td>
                            <td>${anexoHtml}</td>
                        </tr>
                    `;
                }
            } else {
                let ramais = dados.ramal ? dados.ramal.split(',').map(s => s.trim()) : [];
                let locais = dados.local ? dados.local.split(',').map(s => s.trim()) : [];
                let maxLen = Math.max(ramais.length, locais.length, (dados.anexos || []).length);

                if (maxLen > 0) {
                    for(let i = 0; i < maxLen; i++) {
                        let anexo = (dados.anexos || [])[i];
                        let anexoHtml = '-';
                        if (anexo) {
                            anexoHtml = `
                                <div class="d-flex justify-content-center gap-1">
                                    <a href="${anexo.arquivo}" target="_blank" class="btn btn-sm btn-outline-danger" title="Abrir PDF"><i class="bi bi-file-earmark-pdf"></i></a>
                                    ${anexo.id !== 'legacy' ? `<button type="button" class="btn btn-sm btn-outline-danger" onclick="excluirAnexo(${dados.id}, ${anexo.id})" title="Excluir PDF"><i class="bi bi-trash"></i></button>` : ''}
                                </div>
                            `;
                        }

                        tbodyAparelhos.innerHTML += `
                            <tr>
                                <td><span class="text-muted fst-italic">Aguardando Instalação</span></td>
                                <td>${locais[i] || '-'}</td>
                                <td>${ramais[i] || '-'}</td>
                                <td>${anexoHtml}</td>
                            </tr>
                        `;
                    }
                } else {
                    tbodyAparelhos.innerHTML = `<tr><td colspan="4" class="text-muted">Nenhum aparelho vinculado.</td></tr>`;
                }
            }

            // Abre o modal
            const modalEl = document.getElementById('modal-visualizar-solicitacao');
            const modal = new bootstrap.Modal(modalEl);
            modal.show();

        } else {
            Swal.fire("Erro!", "Não foi possível carregar as informações da solicitação.", "error");
        }
    } catch (erro) {
        console.error(erro);
        Swal.fire("Erro!", "Problema de conexão com o servidor.", "error");
    }
};

window.abrirEdicaoSolicitacao = async function(id) {
    try {
        const resposta = await fetch(`/telefonia/api/solicitacoes/${id}/`);
        if (resposta.ok) {
            const dados = await resposta.json();
            
            // Tratamento da data
            const formatDate = (dString) => {
                if(!dString) return '-';
                let d = new Date(dString);
                return d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
            };
            
            document.getElementById('edit-solicitacao-id').value = id;
            document.getElementById('edit-protocolo').value = dados.protocolo || '';
            document.getElementById('edit-data').value = dados.data ? formatDate(dados.data) : '';
            document.getElementById('edit-unidade').value = dados.unidade || '';
            document.getElementById('edit-sigla').value = dados.sigla_unidade || '';
            document.getElementById('edit-local').value = dados.local || '';
            document.getElementById('edit-termo').value = dados.termo_transferencia_interna || '';
            document.getElementById('edit-status').value = dados.status || 'recebida';
            document.getElementById('edit-quantidade').value = dados.qnt_solicitada || '';
            document.getElementById('edit-solicitante').value = dados.solicitante || '';
            document.getElementById('edit-ramal').value = dados.ramal || '';
            document.getElementById('edit-tecnico_responsavel').value = dados.tecnico_responsavel || '';
            document.getElementById('edit-data_instalacao').value = dados.data_instalacao ? dados.data_instalacao.substring(0, 16) : '';
            document.getElementById('edit-relatorio').value = dados.relatorio || '';

            const midiaContainer = document.getElementById('midia-atual-container');
            const linkMidia = document.getElementById('link-midia-atual');
            if (dados.midia) {
                midiaContainer.style.display = 'block';
                linkMidia.href = dados.midia;
            } else {
                midiaContainer.style.display = 'none';
                linkMidia.href = '#';
            }
            // Reset input file
            document.getElementById('edit-midia').value = '';

            const secaoAparelhosEmpty = document.getElementById('edit-secao-aparelhos-empty');
            const tbodyAparelhos = document.getElementById('edit-tbody-aparelhos');
            
            if (dados.aparelhos_detalhes && dados.aparelhos_detalhes.length > 0) {
                secaoAparelhosEmpty.style.display = 'none';
                tbodyAparelhos.innerHTML = '';
                dados.aparelhos_detalhes.forEach(ap => {
                    tbodyAparelhos.innerHTML += `
                        <tr>
                            <td><strong>${ap.patrimonio || '-'}</strong></td>
                            <td>${ap.ramal || '-'}</td>
                        </tr>
                    `;
                });
            } else {
                secaoAparelhosEmpty.style.display = 'block';
                tbodyAparelhos.innerHTML = '';
            }

            const modalEl = document.getElementById('modal-editar-solicitacao');
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        } else {
            Swal.fire("Erro!", "Não foi possível carregar as informações da solicitação.", "error");
        }
    } catch (error) {
        console.error("Erro:", error);
    }
};

window.salvarEdicaoSolicitacao = async function() {
    const id = document.getElementById('edit-solicitacao-id').value;
    
    const formData = new FormData();
    formData.append('unidade', document.getElementById('edit-unidade').value);
    formData.append('sigla_unidade', document.getElementById('edit-sigla').value);
    formData.append('local', document.getElementById('edit-local').value);
    formData.append('termo_transferencia_interna', document.getElementById('edit-termo').value);
    formData.append('status', document.getElementById('edit-status').value);
    formData.append('qnt_solicitada', document.getElementById('edit-quantidade').value);
    formData.append('solicitante', document.getElementById('edit-solicitante').value);
    formData.append('ramal', document.getElementById('edit-ramal').value);
    formData.append('tecnico_responsavel', document.getElementById('edit-tecnico_responsavel').value);
    
    const dataInstal = document.getElementById('edit-data_instalacao').value;
    if (dataInstal) {
        formData.append('data_instalacao', dataInstal);
    }
    
    formData.append('relatorio', document.getElementById('edit-relatorio').value);

    const midiaInput = document.getElementById('edit-midia');
    if (midiaInput && midiaInput.files.length > 0) {
        formData.append('midia', midiaInput.files[0]);
    }

    try {
        const res = await fetch(`/telefonia/api/solicitacoes/${id}/`, {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });

        if (res.ok) {
            bootstrap.Modal.getInstance(document.getElementById('modal-editar-solicitacao')).hide();
            $('#tabela-solicitacoes').DataTable().ajax.reload(null, false);
            // atualizarContadoresSolicitacoes(); // Removido por nao estar definido
            Swal.fire("Sucesso!", "Solicitação atualizada com sucesso.", "success");
        } else {
            console.error(await res.text());
            Swal.fire("Erro!", "Erro ao salvar as edições.", "error");
        }
    } catch (error) {
        console.error("Erro:", error);
        Swal.fire("Erro!", "Ocorreu um erro ao salvar as alterações.", "error");
    }
};

window.visualizarSenha = async function(id) {
    try {
        const resposta = await fetch(`/telefonia/api/senhas/${id}/`);
        if (resposta.ok) {
            const dados = await resposta.json();
            
            const formatDate = (dString) => {
                if(!dString) return '-';
                let d = new Date(dString);
                return d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
            };

            document.getElementById('vis-senha-protocolo').textContent = dados.protocolo || '-';
            document.getElementById('vis-senha-solicitante').textContent = dados.solicitante || '-';
            document.getElementById('vis-senha-unidade').textContent = dados.unidade || '-';
            document.getElementById('vis-senha-sigla').textContent = dados.sigla_unidade ? dados.sigla_unidade.toUpperCase() : '-';
            document.getElementById('vis-senha-registrada').textContent = dados.senha || 'Não informada';
            document.getElementById('vis-senha-edificios').textContent = dados.edificios || '-';
            document.getElementById('vis-senha-usuario').textContent = dados.usuario || '-';
            document.getElementById('vis-senha-ramal').textContent = dados.ramal || '-';
            
            document.getElementById('vis-senha-cargo').textContent = dados.cargo === 'colaborador' ? 'Colaborador' : 'Servidor';
            if (dados.cargo === 'colaborador') {
                document.getElementById('vis-dados-colaborador').style.display = 'block';
                document.getElementById('vis-senha-contrato').textContent = dados.numero_contrato || '-';
                document.getElementById('vis-senha-empresa').textContent = dados.empresa_vinculada || '-';
                document.getElementById('vis-senha-fiscal').textContent = dados.fiscal_contrato || '-';
                document.getElementById('vis-senha-unidade-fiscal').textContent = dados.unidade_fiscal || '-';
            } else {
                document.getElementById('vis-dados-colaborador').style.display = 'none';
            }
            document.getElementById('vis-senha-email').textContent = dados.email || 'Não informado';
            
            document.getElementById('vis-senha-categoria').textContent = dados.categoria || '-';
            document.getElementById('vis-senha-desvio').textContent = dados.desvio ? 'Sim' : 'Não';
            document.getElementById('vis-senha-tel-desvio').textContent = dados.tel_desvio_externo || '-';
            
            document.getElementById('vis-senha-tecnico').textContent = dados.nome_tecnico || 'Não informado';
            document.getElementById('vis-senha-created').textContent = formatDate(dados.created_at);
            document.getElementById('vis-senha-updated').textContent = formatDate(dados.updated_at);
            
            const modalEl = document.getElementById('modal-visualizar-senha');
            const modal = new bootstrap.Modal(modalEl);
            modal.show();

        } else {
            Swal.fire("Erro!", "Não foi possível carregar as informações da senha.", "error");
        }
    } catch (erro) {
        console.error(erro);
        Swal.fire("Erro!", "Problema de conexão com o servidor.", "error");
    }
};

window.visualizarAparelho = async function(id) {
    try {
        const resposta = await fetch(`/gestao_patrimonio/api/aparelhos-telefonicos/${id}/`);
        if (resposta.ok) {
            const dados = await resposta.json();
            
            document.getElementById('vis-ap-patrimonio').textContent = dados.patrimonio || '-';
            document.getElementById('vis-ap-modelo').textContent = dados.modelo || '-';
            document.getElementById('vis-ap-fcn').textContent = dados.fcn || '-';
            document.getElementById('vis-ap-mac').textContent = dados.mac_address || '-';
            
            let htmlIntegridade = '-';
            if (dados.integridade === 'funciona') htmlIntegridade = '<span class="badge bg-success">Funciona</span>';
            else if (dados.integridade === 'defeito') htmlIntegridade = '<span class="badge bg-danger">Defeito</span>';
            else htmlIntegridade = dados.integridade;
            document.getElementById('vis-ap-integridade').innerHTML = htmlIntegridade;

            let htmlStatus = '-';
            if (dados.status === 'estoque') htmlStatus = '<span class="badge bg-secondary">Estoque</span>';
            else if (dados.status === 'instalado') htmlStatus = '<span class="badge bg-primary">Instalado</span>';
            else if (dados.status === 'defeituoso') htmlStatus = '<span class="badge bg-danger">Defeituoso</span>';
            else htmlStatus = dados.status;
            document.getElementById('vis-ap-status').innerHTML = htmlStatus;
            
            document.getElementById('vis-ap-ramal').textContent = dados.ramal || '-';
            document.getElementById('vis-ap-sala').textContent = dados.sala || '-';

            const modalEl = document.getElementById('modal-visualizar-aparelho');
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        } else {
            Swal.fire("Erro!", "Não foi possível carregar os dados do aparelho.", "error");
        }
    } catch (erro) {
        console.error(erro);
        Swal.fire("Erro!", "Problema de conexão com o servidor.", "error");
    }
};

window.aparelhosDefeituososGlobal = [];

window.abrirModalNovaRemessa = async function() {
    try {
        const res = await fetch('/gestao_patrimonio/api/aparelhos-telefonicos/');
        if(res.ok) {
            const aparelhos = await res.json();
            window.aparelhosDefeituososGlobal = aparelhos.filter(ap => ap.status === 'defeituoso' || ap.integridade === 'defeito');
            
            document.getElementById('form-remessa-manutencao').reset();
            const container = document.getElementById('remessa-aparelhos-container');
            if (container) container.innerHTML = '';
            
            // Adiciona a primeira linha vazia
            if (window.renderLinhaAparelhoRemessa) {
                window.renderLinhaAparelhoRemessa(Date.now());
            }

            const modalEl = document.getElementById('modal-remessa-manutencao');
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }
    } catch (e) {
        console.error(e);
        Swal.fire('Erro', 'Não foi possível carregar os aparelhos com defeito.', 'error');
    }
};

window.salvarRemessaManutencao = async function() {
    const form = document.getElementById('form-remessa-manutencao');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const container = document.getElementById('remessa-aparelhos-container');
    const selects = container.querySelectorAll('.select-aparelho-dinamico-remessa');
    const selectedOptions = Array.from(selects).map(sel => sel.value).filter(val => val !== '');
    
    if (selectedOptions.length === 0) {
        Swal.fire('Atenção', 'Selecione ao menos um aparelho.', 'warning');
        return;
    }

    const payload = {
        memorando: document.getElementById('remessa_memorando').value,
        empresa_contratada: document.getElementById('remessa_empresa').value,
        contrato_tse: document.getElementById('remessa_contrato').value,
        aparelhos: selectedOptions
    };

    try {
        const response = await fetch('/telefonia/api/remessas/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            $('#modal-remessa-manutencao').modal('hide');
            $('#tabela-remessas').DataTable().ajax.reload();
            Swal.fire('Sucesso!', 'Remessa salva com sucesso.', 'success');
        } else {
            const errorData = await response.json();
            console.error('Erro na requisição:', errorData);
            Swal.fire('Erro!', 'Não foi possível salvar a remessa.', 'error');
        }
    } catch (erro) {
        console.error(erro);
        Swal.fire('Erro!', 'Problema de conexão com o servidor.', 'error');
    }
};

window.enviarEmailSenha = async function(id) {
    const result = await Swal.fire({
        title: 'Enviar Senha por E-mail?',
        text: 'Deseja realmente notificar o usuário enviando a senha telefônica para o e-mail institucional?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sim, enviar e-mail!',
        cancelButtonText: 'Cancelar'
    });

    if (!result.isConfirmed) return;

    try {
        Swal.fire({
            title: 'Enviando E-mail...',
            text: 'Por favor, aguarde.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        
        const response = await fetch(`/telefonia/senha/${id}/email/`);
        const responseData = await response.json();
        
        if (response.ok) {
            Swal.fire('Enviado!', responseData.message || 'E-mail enviado com sucesso.', 'success');
        } else {
            Swal.fire('Erro!', responseData.error || 'Erro ao enviar o e-mail.', 'error');
        }
    } catch (error) {
        console.error(error);
        Swal.fire('Erro!', 'Problema de conexão com o servidor.', 'error');
    }
};


window.contratosColaboradorCache = [];

// Carrega os contratos na inicialização
async function carregarContratos() {
    try {
        const res = await fetch('/telefonia/api/contratos/');
        if (res.ok) {
            window.contratosColaboradorCache = await res.json();
            const select = document.getElementById('select_contrato_senha');
            if (select) {
                // Limpar opções existentes, mantendo as duas primeiras (Selecione e Novo)
                select.innerHTML = '<option value="">-- Selecione --</option><option value="novo">+ Novo Contrato</option>';
                window.contratosColaboradorCache.forEach(c => {
                    select.innerHTML += `<option value="${c.numero_contrato}">${c.numero_contrato}</option>`;
                });
            }
        }
    } catch(e) {
        console.error("Erro ao carregar contratos", e);
    }
}
document.addEventListener('DOMContentLoaded', carregarContratos);

window.toggleColaboradorFields = function(cargo) {
    const container = document.getElementById('dados_colaborador_container');
    if (cargo === 'colaborador') {
        container.style.display = 'block';
        if (window.contratosColaboradorCache.length === 0) {
            carregarContratos();
        }
    } else {
        container.style.display = 'none';
        // Limpar os campos ao esconder
        document.getElementById('numero_contrato_senha').value = '';
        document.getElementById('empresa_vinculada_senha').value = '';
        document.getElementById('fiscal_contrato_senha').value = '';
        document.getElementById('unidade_fiscal_senha').value = '';
        document.getElementById('select_contrato_senha').value = '';
    }
};

window.mudarContrato = function(valor) {
    const divNovo = document.getElementById('div_numero_contrato_novo');
    const inputNumero = document.getElementById('numero_contrato_senha');
    const inputEmpresa = document.getElementById('empresa_vinculada_senha');
    const inputFiscal = document.getElementById('fiscal_contrato_senha');
    const inputUnidade = document.getElementById('unidade_fiscal_senha');

    if (valor === 'novo') {
        divNovo.style.display = 'block';
        inputNumero.value = '';
        inputEmpresa.value = '';
        inputFiscal.value = '';
        inputUnidade.value = '';
        
        inputNumero.readOnly = false;
        inputEmpresa.readOnly = false;
        inputFiscal.readOnly = false;
        inputUnidade.readOnly = false;
    } else if (valor === '') {
        divNovo.style.display = 'none';
        inputNumero.value = '';
        inputEmpresa.value = '';
        inputFiscal.value = '';
        inputUnidade.value = '';
        
        inputNumero.readOnly = false;
        inputEmpresa.readOnly = false;
        inputFiscal.readOnly = false;
        inputUnidade.readOnly = false;
    } else {
        divNovo.style.display = 'none';
        const contrato = window.contratosColaboradorCache.find(c => c.numero_contrato === valor);
        if (contrato) {
            inputNumero.value = contrato.numero_contrato;
            inputEmpresa.value = contrato.empresa_vinculada || '';
            inputFiscal.value = contrato.fiscal_contrato || '';
            inputUnidade.value = contrato.unidade_fiscal || '';
            
            // Trava para evitar edição
            inputNumero.readOnly = true;
            inputEmpresa.readOnly = true;
            inputFiscal.readOnly = true;
            inputUnidade.readOnly = true;
        }
    }
}

// Funções de Deleção
function deletarSolicitacao(id) {
    Swal.fire({
        title: 'Tem certeza?',
        text: "Deseja realmente deletar esta solicitação? Esta ação não pode ser desfeita.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, deletar!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/telefonia/api/solicitacoes/${id}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            }).then(response => {
                if (response.ok) {
                    Swal.fire('Deletado!', 'Solicitação deletada com sucesso.', 'success');
                    $('#tabela-solicitacoes').DataTable().ajax.reload(null, false);
                } else {
                    Swal.fire('Erro!', 'Ocorreu um erro ao deletar.', 'error');
                }
            });
        }
    });
}

function deletarAparelho(id) {
    Swal.fire({
        title: 'Tem certeza?',
        text: "Deseja realmente deletar este aparelho? Esta ação não pode ser desfeita.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, deletar!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/gestao_patrimonio/api/aparelhos-telefonicos/${id}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            }).then(response => {
                if (response.ok) {
                    Swal.fire('Deletado!', 'Aparelho deletado com sucesso.', 'success');
                    $('#tabela-aparelhos').DataTable().ajax.reload(null, false);
                } else {
                    Swal.fire('Erro!', 'Ocorreu um erro ao deletar.', 'error');
                }
            });
        }
    });
};

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

// Fase Administrativa
function abrirModalFinalizarAdministrativo(id) {
    $('#id_finalizacao_admin').val(id);
    $('#form-finalizar-administrativo')[0].reset();
    
    const tbody = document.getElementById('tbody-finalizar-aparelhos');
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="4"><div class="spinner-border spinner-border-sm text-primary" role="status"></div> Carregando...</td></tr>';
    }
    
    $('#modal-finalizar-administrativo').modal('show');
    
    fetch(`/telefonia/api/solicitacoes/${id}/`)
        .then(response => response.json())
        .then(dados => {
            if (!tbody) return;
            tbody.innerHTML = '';
            let html = '';
            if (dados.aparelhos_detalhes && dados.aparelhos_detalhes.length > 0) {
                dados.aparelhos_detalhes.forEach(ap => {
                    html += `
                        <tr>
                            <td><strong>${ap.patrimonio || '-'}</strong></td>
                            <td>${ap.sala || '-'}</td>
                            <td>${ap.ramal || '-'}</td>
                            <td><input type="file" name="pdf_termos" accept="application/pdf" class="form-control form-control-sm" required></td>
                        </tr>
                    `;
                });
            } else {
                let ramais = dados.ramal ? dados.ramal.split(',').map(s => s.trim()) : [];
                let locais = dados.local ? dados.local.split(',').map(s => s.trim()) : [];
                let maxLen = Math.max(ramais.length, locais.length);
                if (maxLen > 0) {
                    for(let i = 0; i < maxLen; i++) {
                        html += `
                            <tr>
                                <td><span class="text-muted fst-italic">Aguardando Instalação</span></td>
                                <td>${locais[i] || '-'}</td>
                                <td>${ramais[i] || '-'}</td>
                                <td><input type="file" name="pdf_termos" accept="application/pdf" class="form-control form-control-sm" required></td>
                            </tr>
                        `;
                    }
                } else {
                    html = `<tr><td colspan="4" class="text-muted">Nenhum aparelho vinculado.</td></tr>`;
                }
            }
            tbody.innerHTML = html;
        })
        .catch(err => {
            if (tbody) tbody.innerHTML = '<tr><td colspan="4" class="text-danger">Erro ao carregar aparelhos.</td></tr>';
        });
}

document.addEventListener("DOMContentLoaded", function() {
    $('#form-finalizar-administrativo').on('submit', function(e) {
        e.preventDefault();
        const id = $('#id_finalizacao_admin').val();
        let formData = new FormData(this);

        Swal.fire({
            title: 'Enviando...',
            allowOutsideClick: false,
            didOpen: () => { Swal.showLoading(); }
        });

        fetch(`/telefonia/api/solicitacoes/${id}/finalizar_administrativo/`, {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(result => {
            if (result.status === 200 || result.status === 201) {
                Swal.fire('Sucesso!', 'Demanda finalizada administrativamente.', 'success');
                $('#modal-finalizar-administrativo').modal('hide');
                $('#tabela-solicitacoes').DataTable().ajax.reload(null, false);
            } else {
                Swal.fire('Erro!', result.body.detail || 'Ocorreu um erro ao finalizar.', 'error');
            }
        })
        .catch(error => {
            Swal.fire('Erro!', 'Erro de conexão com o servidor.', 'error');
        });
    });
});

function copyToClipboardFallback(text) {
    var textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
        document.execCommand('copy');
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }
    document.body.removeChild(textArea);
}

window.copiarPatrimonio = function(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            Swal.fire({toast: true, position: 'top-end', icon: 'success', title: 'Copiado!', showConfirmButton: false, timer: 1500});
        }).catch(err => {
            copyToClipboardFallback(text);
            Swal.fire({toast: true, position: 'top-end', icon: 'success', title: 'Copiado!', showConfirmButton: false, timer: 1500});
        });
    } else {
        copyToClipboardFallback(text);
        Swal.fire({toast: true, position: 'top-end', icon: 'success', title: 'Copiado!', showConfirmButton: false, timer: 1500});
    }
};

window.excluirAnexo = function(solicitacaoId, anexoId) {
    Swal.fire({
        title: 'Tem certeza?',
        text: "Esta ação irá deletar o documento PDF permanentemente!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sim, deletar!'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({title: 'Excluindo...', allowOutsideClick: false, didOpen: () => { Swal.showLoading(); }});
            fetch(`/telefonia/api/solicitacoes/${solicitacaoId}/excluir_anexo/${anexoId}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            })
            .then(res => res.json().then(data => ({ status: res.status, body: data })))
            .then(result => {
                if (result.status === 200) {
                    Swal.fire('Excluído!', 'O anexo foi excluído com sucesso.', 'success');
                    // Reload modal data
                    visualizarSolicitacao(solicitacaoId);
                } else {
                    Swal.fire('Erro!', result.body.error || 'Erro ao excluir.', 'error');
                }
            })
            .catch(() => Swal.fire('Erro!', 'Problema de conexão com o servidor.', 'error'));
        }
    });
}
