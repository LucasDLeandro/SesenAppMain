import {formatDataIso, mesAnoAtual} from './utils.js';

const ordensAbertas = document.getElementById('tabela-elev-ordens-abertas')
new DataTable(ordensAbertas, {
    info: true,
    language: {
        url: 'https://cdn.datatables.net/plug-ins/2.0.3/i18n/pt-BR.json'
    },
    order: [],
    layout: {
        topStart: 'pageLength',
        topEnd: 'search'
    },
    responsive: true
});

const ordens_concluidas = document.getElementById('ordens-concluidas-tab')

ordens_concluidas.addEventListener('click', async function() {

    const urlElevDados = '/ordens/api/os/listaOs/api_elev_concluidas'

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
                    <td>${os.ocorrencia}</td>
                    <td>${os.solicitante}</td>
                    <td>${os.data_hora_chegada || 'N/A'}</td>
                    <td>${os.tmp_chegada} min</td>
                    <td>${os.data_hora_saida || 'N/A'}</td>
                    <td>${os.tmp_saida} min</td> 
                    <td>${os.componente}</td>
                    <td>${os.sub_componente}</td>
                    <td>${os.tempo_parado}h</td>
                    <td>${os.servico}</td>
                    <td>
                        <span class="badge bg-success">${os.status}</span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="{abrirModalElevConcluir(${ os.id }, ${ os.protocolo })}" title="ConcluirOs">
                            <i class="bi bi-pencil-square"></i> Editar
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
            columnDefs: [
                {
                    targets: [3, 12],
                    render: function (data, type, row) {
                        // Se a ação for 'display' (exibir na tela) e o texto tiver mais de 50 letras
                        if (type === 'display' && data && data.length > 35) {
                            
                            // Corta o texto nos primeiros 50 caracteres e adiciona os 3 pontinhos
                            let textoCortado = data.substr(0, 50) + '...';
                            
                            // O 'title' cria a caixa de leitura ao passar o mouse!
                            return `<span title="${data}" style="cursor: pointer;">${textoCortado}</span>`;
                        }
                        
                        // Se for um texto curto, devolve ele normal
                        return data;
                    }
                }
            ]
        });
    } catch (erro) {
        console.error("Erro ao carregar os dados da tabela:", erro);
    }
})

let chartTotalAnual = null

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
    
    dadosTabelaQntOsAnual()
})






