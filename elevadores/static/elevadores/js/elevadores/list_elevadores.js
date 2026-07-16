import {formatDataIso, mesAnoAtual} from './utils.js';

// Função utilitária para aplicar filtros de pesquisa individual por coluna
function aplicarFiltroColunas(tabela) {
    var tableNode = tabela.table().node();
    var thead = tableNode.querySelector('thead');
    
    // Verifica se a linha de filtros já existe para evitar duplicidade
    if (thead.querySelector('.filter-row')) return;

    var tr = document.createElement('tr');
    tr.className = 'filter-row';

    tabela.columns().every(function(index) {
        var column = this;
        var headerText = column.header().textContent.trim();
        var th = document.createElement('th');

        if (headerText.toLowerCase() === 'ações' || headerText.toLowerCase() === 'acões' || headerText === '') {
            tr.appendChild(th);
            return;
        }

        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control form-control-sm';
        input.placeholder = 'Filtrar ' + headerText;
        input.style.cssText = 'width:100%;font-size:12px;padding:4px 8px;border:1px solid #ced4da;border-radius:4px;background-color:#f8f9fa';

        var debounceTimer;
        input.addEventListener('keyup', function() {
            var self = this;
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function() {
                if (column.search() !== self.value) {
                    column.search(self.value).draw();
                }
            }, 300);
        });

        input.addEventListener('click', function(e) { e.stopPropagation(); });

        th.appendChild(input);
        tr.appendChild(th);
    });

    thead.appendChild(tr);
}

const ordensAbertas = document.getElementById('tabela-elev-ordens-abertas')
if (ordensAbertas) {
    new DataTable(ordensAbertas, {
        info: true,
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
        order: [],
        layout: {
            topStart: 'pageLength',
            topEnd: 'search'
        },
        responsive: true,
        orderCellsTop: true,
        initComplete: function() {
            aplicarFiltroColunas(this.api());
        }
    });
}

const ordens_concluidas = document.getElementById('ordens-concluidas-tab')

ordens_concluidas.addEventListener('click', async function() {

    //const urlElevDados = '/elevadores/api/os/listaOs/api_elev_concluidas'
    const urlElevDados = '/elevadores/api/elevadoress/elev_oss_concluidas/'

    try {
        const resposta = await fetch(urlElevDados)

        const dados_api = await resposta.json()

        const corpoTabela = document.getElementById('tabela-oss-completa')
        corpoTabela.innerHTML = ''

        let todoOConteudoHTML = ''

        dados_api.tabela_concluidas.forEach(os => {
            const linhaHTML = `
                <tr>
                    <td><code>${os.protocolo}</code></td>
                    <td class="text-nowrap">${os.data_hora}</td>
                    <td> <span class="bg-light-subtle text-dark-emphasis">${os.elevador}</span></td>
                    <td>${os.tmp_chegada} min</td>
                    <td>
                        <span class="badge bg-success">${os.status}</span>
                    </td>
                    <td class="text-nowrap text-end">
                        <button class="btn btn-sm btn-outline-primary" style="white-space: nowrap;" onclick="abrirModalVisualizarElev(&quot;${os.protocolo || ''}&quot;, &quot;${os.data_hora || ''}&quot;, &quot;${os.elevador || ''}&quot;, &quot;${String(os.ocorrencia || '').replace(/\\n/g, ' ').replace(/\"/g, '&amp;quot;')}&quot;, &quot;${os.aprisionamento ? 'Sim' : 'Não'}&quot;, &quot;${os.solicitante || ''}&quot;, &quot;${os.atendente || ''}&quot;, &quot;${os.status || ''}&quot;, &quot;${os.elevador_parado || (os.tempo_parado + 'h')}&quot;, &quot;${os.data_hora_chegada || ''}&quot;, &quot;${os.data_hora_saida || ''}&quot;, &quot;${os.tmp_chegada || ''}&quot;, &quot;${os.tmp_saida || ''}&quot;, &quot;${os.tecnico || ''}&quot;, &quot;${os.componente || ''}&quot;, &quot;${os.sub_componente || ''}&quot;, &quot;${String(os.servico || '').replace(/\\n/g, ' ').replace(/\"/g, '&amp;quot;')}&quot;)" title="Visualizar O.S">
                            <i class="bi bi-eye me-1"></i> Visualizar
                        </button>
                    </td>
                </tr>
            `
            todoOConteudoHTML += linhaHTML
            
        })

        if ($.fn.DataTable.isDataTable('#tabela-principal')) {
            $('#tabela-principal').DataTable().destroy();
        }

        corpoTabela.innerHTML = todoOConteudoHTML

        
        const tabelaOrdens = document.getElementById('tabela-principal')
        new DataTable(tabelaOrdens, {
            info: true,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/2.0.3/i18n/pt-BR.json'
            },
            layout: {
                topStart: 'pageLength',
                topEnd: 'search'
            },
            order: [],
            responsive: true,
            orderCellsTop: true,
            initComplete: function() {
                aplicarFiltroColunas(this.api());
            }
        });
    } catch (erro) {
        console.error("Erro ao carregar os dados da tabela:", erro);
    }
})

/*let chartTotalAnual = null

async function dadosTabelaQntOsAnual() {
    const data_inicio = document.getElementById('dash-data-inicio') 

    const {ano_atual} = mesAnoAtual()
    
    let anoFiltrado = ""
    if (data_inicio.value === "") {
        anoFiltrado = ano_atual
        
    } else {
        anoFiltrado = data_inicio.value.substring(0,4)
    }
    
    const urlElevGrafico = '/ordens/api/os/graficoMensal/'
    const params = new URLSearchParams()

    params.append('ano', anoFiltrado)
    

    let urlFiltrada = urlElevGrafico

    const strParams = params.toString()
    urlFiltrada = urlElevGrafico + '?' + strParams

    try {
        const resposta = await fetch(urlFiltrada)

        const dados_api = await resposta.json()

        const corpoChart = document.getElementById('chart-5')

        const corpoTabela = document.getElementById('tabela-cont-os')

        corpoTabela.innerHTML = ''

        let todoOConteudoHTML = dados_api.df_html

        corpoTabela.innerHTML = todoOConteudoHTML;

        const table_teste = document.getElementById('tabela-cont-os-elev')

        new DataTable(table_teste, {
            paging: false,
            searching: false,
            info: false,
            language: {
                url: 'https://cdn.datatables.net/plug-ins/2.0.3/i18n/pt-BR.json'
            },
        });

        let options = {
            chart: {
                type: 'bar',
                height: '100%',
                width: '100%',
                toolbar: {
                    show: true
                },
                events: {
                    dataPointSelection: function(event, chartContext, config) {
                        
                    }
                }
            },
            series: [{
                name: 'Quantidade',
                data: dados_api.series,
                
            }],
            dataLabels: {
                enabled: true,
                style: {
                    fontSize: '14px'
                }
            },
            plotOptions: {
                bar: {
                    borderRadius: 2,
                    dataLabels: {
                        position: 'center'
                    }
                }
            },
            
            xaxis: {
                categories: dados_api.meses,
                title: {
                    text: ''
                },
                labels: {
                    style: {
                        fontSize: '13px',
                        fontWeigth: 600,
                        colors: '#777777'
                    }
                }
            },
            legend: {
                show: true,
                fontSize: '50px'
            }, 
            colors: ['#25CCFF', '#F44336', '#E91E63', '#9C27B0'],
            states: {
                hover: {
                    filter: {
                        type: 'darken',
                        value: 0.2
                    }
                },
                active: {
                    filter: {
                        type: 'darken',
                        value: 0.3
                    }
                }
            },
            tooltip: {
                enabled: true,
                theme: 'ligth',
                style: {
                    fontSize: '14px'
                }
            }
            
        }

        if (chartTotalAnual !== null) {
            chartTotalAnual.destroy()
        }

        chartTotalAnual = new ApexCharts(corpoChart, options)
        chartTotalAnual.render()

    } catch (erro) {
        console.error("Erro ao carregar os dados da tabela:", erro);
    }

}

const elev_tab_dash = document.getElementById('elev-tab-dash')
elev_tab_dash.addEventListener('click', () => {
    
    //dadosTabelaQntOsAnual()
})*/






