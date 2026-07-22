import {formatDataIso, mesAnoAtual, filtroAnosMeses, changeFiltro, listaElevadores} from './utils.js';

const elev_selecionado = document.getElementById('dash-elevador')

const {inicioMesAtual, fimMesAtual, rangeDeAnos, rangeDeMeses, inicioAnoAtual, fimAnoAtual} = mesAnoAtual()


const urlBase = "/elevadores/api/elevadoress/dashboard/"


export let dados_api = {}
export async function loadDataDashboard({...kwargs}) {

    const params = new URLSearchParams();
    if (kwargs.inicio) {
        params.append('inicio', kwargs.inicio)
    } 
    if (kwargs.fim) {
        params.append('fim', kwargs.fim)
    }
    if (elev_selecionado) {
        params.append('elev', elev_selecionado.value)
    } 
    
    let urlFiltrada = urlBase
    const strParams = params.toString();
    if (strParams != "") {
        urlFiltrada = urlBase + '?' + strParams  
    }
    
    try {
        const resposta = await fetch(urlFiltrada)
        dados_api = await resposta.json()

        console.log(dados_api)

        return dados_api

    } catch (erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }
    
}


async function dadosIndicadorUm() {

    const filtroDinamicoChartUm = document.getElementById('filtro-dinamico-chart-1')
    const corpoChartUm = document.getElementById('chart-1')

    try {
        const categoriasX = dados_api.ind_um.map(item => item.protocolo)
        const dadosY = dados_api.ind_um.map(item => item.min_chegada)

        const textoFormatado = dadosY.map(valor => `${valor}min`)

        const customData = categoriasX.map(protocolo => {
            const dadosOs = dados_api.ind_um.find(item => item.protocolo === protocolo)
            if(dadosOs) {
                return [
                    `${dadosOs.protocolo}`,
                    `${dadosOs.elevador}`,
                    `${dadosOs.data_hora}`,
                    `${dadosOs.min_chegada}`,
                    `${dadosOs.meta_pp}`,
                    `${dadosOs.meta_comum}`,
                ]
            } else {
                return [
                    protocolo,
                    '-',
                    '-',
                    '-',
                    '-',
                    '-'
                ]
            }
        })

        filtroAnosMeses(filtroDinamicoChartUm, rangeDeAnos, rangeDeMeses)

        const dadosPlotly = [{
            x: categoriasX,
            y: dadosY,
            customdata: customData,
            type: 'bar',
            text: textoFormatado,
            hovertemplate: 
                'Procotolo: <b>%{customdata[0]}</b><br><br>' +
                'Elevador: <b>%{customdata[1]}</b><br>' +
                'Data OS: <b>%{customdata[2]}</b><br>' +
                'Tempo ACE: <b>%{customdata[3]}min</b><br>' +
                'Meta Com Aprisionamento: <b>%{customdata[4]}min</b><br>' +
                'Meta sem Aprisionamento : <b>%{customdata[5]}min</b>' +
                '<extra></extra>',
            textposition: 'auto',

            textfont: {
                size: 16,
                weight: 'bold'
            }
        }]
        

        const layoutChartUm = { margin: { l: 40, r: 20, t: 30, b: 40 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { family: 'Inter, sans-serif' }, colorway: ['#4e73df', '#1cc88a', '#36b9cc'], hovermode: 'closest', xaxis: { showgrid: false,
                type: 'category',
            },
            height: 500
        }
            
        

        Plotly.react(corpoChartUm, dadosPlotly, layoutChartUm)

        filtroDinamicoChartUm.addEventListener('change', async function(event) {
            
            if (event.target.classList.contains('filtro-mes')) {
        
                const isMarcado = event.target.checked
                const anoMesSelecionado = event.target.getAttribute('data-ano')
                const anoDesteMes = filtroDinamicoChartUm.querySelector(`.filtro-ano[value="${anoMesSelecionado}"]`)
                
        
                const todosCheckboxes = filtroDinamicoChartUm.querySelectorAll('input[type="checkbox"]')
        
                let data_inicio = null
                let data_fim = null
        
                if (isMarcado) {
                    anoDesteMes.checked = true
                    const ano = anoDesteMes.value
                    const mes = event.target.value.substring(5,7)
        
                    data_inicio = `${ano}-${mes}-01`
                    const ultimoDiaMes = new Date(ano, mes, 0).getDate()
                    data_fim = `${ano}-${mes}-${ultimoDiaMes}`

                    const dadosFiltrados = await loadDataDashboard({inicio: data_inicio, fim: data_fim})

                    const novaCatX = dadosFiltrados.ind_um.map(item => item.protocolo)
                    const novaDadosY = dadosFiltrados.ind_um.map(item => item.min_chegada)

                    const textoFormatado = novaDadosY.map(valor => `${valor}min`)

                    const dataCustom = novaCatX.map(protocolo => {
                        const dadosOs = dadosFiltrados.ind_um.find(item => item.protocolo === protocolo)
                        
                        return [
                            `${dadosOs.protocolo}`,
                            `${dadosOs.elevador}`,
                            `${dadosOs.data_hora}`,
                            `${dadosOs.min_chegada}`,
                            `${dadosOs.meta_pp}`,
                            `${dadosOs.meta_comum}`,
                        ]
                        
                    })
        
                    const novoTraceChartUm = [{
                        x: novaCatX,
                        y: novaDadosY,
                        customdata: dataCustom,
                        type: 'bar',
                        text: textoFormatado,
                        hovertemplate: 
                            'Procotolo: <b>%{customdata[0]}</b><br><br>' +
                            'Elevador: <b>%{customdata[1]}</b><br>' +
                            'Data OS: <b>%{customdata[2]}</b><br>' +
                            'Tempo ACE: <b>%{customdata[3]}min</b><br>' +
                            'Meta Com Aprisionamento: <b>%{customdata[4]}min</b><br>' +
                            'Meta sem Aprisionamento : <b>%{customdata[5]}min</b>' +
                            '<extra></extra>',
                        textposition: 'auto',

                        textfont: {
                            size: 16,
                            weight: 'bold'
                        }
                    }]
                       
                    
        
                    Plotly.react(corpoChartUm, novoTraceChartUm, layoutChartUm)
        
                    todosCheckboxes.forEach(checkbox => {
                        if (checkbox.checked === false) {
                            checkbox.disabled = true
                        }
                    
                    }) 
                    
        
                } else {
                    todosCheckboxes.forEach(checkbox => {
                        checkbox.disabled = false
                    })
        
                    anoDesteMes.checked = false
                    
                    // Restaura os dados padrão
                    Plotly.react(corpoChartUm, dadosPlotly, layoutChartUm)
                }   

            }     
        })




    } catch (erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }
}

async function dadosIndicadorTres() {
    
    const filtroDinamicoChartTres = document.getElementById('filtro-dinamico-chart-3')
    const corpoChartTres = document.getElementById('chart-3')
    
    try {  
        
        filtroAnosMeses(filtroDinamicoChartTres, rangeDeAnos, rangeDeMeses)

       const dadosPlotly = dados_api.ind_tres.map(seriePandas => {
            return {
                name: seriePandas.name,
                x: seriePandas.x,
                y: seriePandas.x.map(() => seriePandas.name),
                customdata: seriePandas.x.map((_, index) => {
                    return [
                        seriePandas.protocolo[index]
                    ]
                }),
                mode: 'markers',
                type: 'scatter',
                marker: {
                    symbol: 'square',
                    size: seriePandas.y.map(ocorrencias => ocorrencias *15),
                    sizemode: 'area',
                    sizeref: 0.1,
                    opacity: 0.7,
                    line: { width: 1, color: 'black' }
                },
                text: seriePandas.y,
                hovertemplate: '<b>Protocolo:</b> %{customdata[0]}<br><b>Data:</b> %{x}<br><b>Elevador:</b> %{y}<br><b>ICR =</b> %{text}<extra></extra>'
                
            }
            
        })
        
        
        const layout = {
            
            xaxis: { 
                type: 'date',
                tickformat: '%d/%m', // Formatação brasileira
                dtick: 86400000,
                showgrid: true,
                gridcolor:'#f0f0f0',
                range: [inicioMesAtual, fimMesAtual],
            },
            yaxis: { 
                type: 'category',
                categoryorder: 'array',
                categoryarray: [...listaElevadores],
                title: 'Quantidade de Ocorrências',
                tickmode: 'linear',
                dtick: 0.1,
                automargin: true,
                autorange: false,
                range: [-0.5, listaElevadores.length -0.5]
                
            },
            showlegend: false, // Ligamos a legenda para você poder filtrar clicando
            height: 500,
            margin: { l: 50, r: 20, t: 50, b: 50 }, // Margens mais limpas
            hovermode: 'closest' // O tooltip foca na bolha exata que o mouse encostar
        }
        
        Plotly.react(corpoChartTres, dadosPlotly, layout)
        
        filtroDinamicoChartTres.addEventListener('change', async function(event) {
            if (event.target.classList.contains('filtro-mes')) {
        
                const isMarcado = event.target.checked
                const anoMesSelecionado = event.target.getAttribute('data-ano')
                const anoDesteMes = filtroDinamicoChartTres.querySelector(`.filtro-ano[value="${anoMesSelecionado}"]`)
                
        
                const todosCheckboxes = filtroDinamicoChartTres.querySelectorAll('input[type="checkbox"]')
        
                let data_inicio = null
                let data_fim = null
        
                if (isMarcado) {
                    anoDesteMes.checked = true
                    const ano = anoDesteMes.value
                    const mes = event.target.value.substring(5,7)
        
                    data_inicio = `${ano}-${mes}-01`
                    const ultimoDiaMes = new Date(ano, mes, 0).getDate()
                    data_fim = `${ano}-${mes}-${ultimoDiaMes}`
        
                    const dadosFiltrados = await loadDataDashboard({inicio: data_inicio, fim: data_fim})
                    const novoPlotly = dadosFiltrados.ind_tres.map(seriePandas => {
                        return {
                            name: seriePandas.name,
                            x: seriePandas.x,
                            y: seriePandas.x.map(() => seriePandas.name),
                            customdata: seriePandas.x.map((_, index) => [seriePandas.protocolo[index]]),
                            mode: 'markers',
                            type: 'scatter',
                            marker: {
                                symbol: 'square',
                                size: seriePandas.y.map(ocorrencias => ocorrencias *15),
                                sizemode: 'area',
                                sizeref: 0.1,
                                opacity: 0.7,
                                line: { width: 1, color: 'black' }
                            },
                            text: seriePandas.y,
                            hovertemplate: '<b>Protocolo:</b> %{customdata[0]}<br><b>Data:</b> %{x}<br><b>Elevador:</b> %{y}<br><b>ICR =</b> %{text}<extra></extra>'
                        }
                    })
                    layout.xaxis.range = [data_inicio, data_fim];
                    Plotly.react(corpoChartTres, novoPlotly, layout)

        
                    todosCheckboxes.forEach(checkbox => {
                        if (checkbox.checked === false) {
                            checkbox.disabled = true
                        }
                    }) 
                    
        
                } else {
                    todosCheckboxes.forEach(checkbox => {
                        checkbox.disabled = false
                    })
        
                    anoDesteMes.checked = false
                    
                    // Restaura o layout para o mês atual e recarrega os dados padrão
                    layout.xaxis.range = [inicioMesAtual, fimMesAtual]
                    Plotly.react(corpoChartTres, dadosPlotly, layout)
                }   

            }     
        }) 
    } catch (erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }
}


async function dadosVisaoGeral() {
    const corpoChart = document.getElementById('chart-5')
    try {
        const eixoX = dados_api.totalizacao[4]['mes_exato']
        const eixoY = dados_api.totalizacao[4]['total_mes']

        const dataInicio = new Date(inicioAnoAtual);
        dataInicio.setDate(dataInicio.getDate() - 15);
        const inicioAjustado = dataInicio.toISOString().split('T')[0]; // Formato YYYY-MM-DD

        const dataFim = new Date(fimAnoAtual);
        dataFim.setDate(dataFim.getDate() + 15);
        const fimAjustado = dataFim.toISOString().split('T')[0];

        const dadosPlotly = [
            {
                x: eixoX,
                y: eixoY,
                type: 'bar',
                text: eixoY
            }
        ]

        const layout = {
            xaxis: {
                type: 'date',
                tickformat: '%m/%Y',
                dtick: 'M1',
                range: [inicioAjustado, fimAjustado],
            },
            yaxis: {
                title: 'total',
                tickmode: 'linear',
                automargin: true,
                //autorange: false,
                //rangemode: 'tozero'
            },
            height: 500,

        }

        Plotly.react(corpoChart, dadosPlotly, layout)

        // Preenche a tabela HTML
        const tabelaContainer = document.getElementById('tabela-cont-os');
        if (tabelaContainer && dados_api.totalizacao && dados_api.totalizacao.length > 3) {
            let tableHtml = dados_api.totalizacao[3];
            // Melhorias visuais usando replace
            tableHtml = tableHtml.replace(/border="1"/g, 'border="0"');
            tableHtml = tableHtml.replace(/<thead([^>]*)>/gi, '<thead class="custom-thead">');
            tableHtml = tableHtml.replace(/style="text-align: right;"/gi, '');
            tableHtml = tableHtml.replace(/<th([^>]*)>/gi, '<th class="text-center align-middle">');
            tableHtml = tableHtml.replace(/<td([^>]*)>/gi, '<td class="text-center align-middle fw-semibold text-secondary">');
            
            tabelaContainer.innerHTML = tableHtml;
        }

    } catch(erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }

}


const elev_tab_dash = document.getElementById('elev-tab-dash')
if (elev_tab_dash) {
    elev_tab_dash.addEventListener('click', async () => {
        await loadDataDashboard({inicio: inicioMesAtual, fim: fimMesAtual})
        dadosVisaoGeral();
        dadosIndicadorUm();
        dadosIndicadorDois();
        dadosIndicadorTres();
        dadosIndicadorQuatro();
        atualizarCardsIndicadores();
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    const tabDashContent = document.getElementById('tab3-content');
    if (tabDashContent && tabDashContent.classList.contains('active')) {
        await loadDataDashboard({inicio: inicioMesAtual, fim: fimMesAtual});
        dadosVisaoGeral();
        dadosIndicadorUm();
        dadosIndicadorDois();
        dadosIndicadorTres();
        dadosIndicadorQuatro();
        atualizarCardsIndicadores();
    }
    
    // Iniciar monitoramento de status dos elevadores
    initStatusElevadores();
});

async function dadosIndicadorQuatro() {
    const filtroDinamicoChartQuatro = document.getElementById('filtro-dinamico-chart-4');
    const corpoChartQuatro = document.getElementById('chart-4');
    if(!corpoChartQuatro) return;
    try {
        if(filtroDinamicoChartQuatro) {
            filtroAnosMeses(filtroDinamicoChartQuatro, rangeDeAnos, rangeDeMeses);
        }
        
        const nomesElevadores = [...listaElevadores];
        const valDisp = listaElevadores.map(nomeElevador => {
            const achou = dados_api.ind_quatro.find(item => item.elevador === nomeElevador)
            return achou ? achou.disponibilidade : 0
        });
        const textFormat = valDisp.map(v => `${v}%`)
        
        const dataCustom = listaElevadores.map(nomeElevador => {
            const achou = dados_api.ind_quatro.find(item => item.elevador === nomeElevador)
            if (achou) {
                return [achou.elevador, achou.tempo_parado, achou.total_mes, achou.dias_uteis, achou.horas_disponiveis]
            } else {
                return [nomeElevador, '-', '-', '-', '-']
            }
        })
        
        const novoTraceChartQuatro = [{
            x: nomesElevadores,
            y: valDisp,
            customdata: dataCustom,
            type: 'bar',
            text: textFormat,
            marker: { color: 'rgba(16, 185, 129, 0.85)', line: { color: '#059669', width: 1 } },
            hovertemplate: 
                'Elevador: <b>%{customdata[0]}</b><br><br>' +
                'Tempo Parado: <b>%{customdata[1]}</b><br>' +
                'Hrs úteis no Mês Total: <b>%{customdata[2]}</b><br>' +
                'Dias úteis no Mês Total: <b>%{customdata[3]}</b><br>' +
                'Horas Disponíveis: <b>%{customdata[4]}</b><br>' +
                'Disponibilidade: <b>%{y}%</b>' +
                '<extra></extra>',
            textposition: 'auto',
            textfont: { size: 14, weight: 'bold', color: '#1e293b' }
        }]
        
        const layoutChartQuatro = { margin: { l: 50, r: 20, t: 30, b: 50 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { family: 'Inter, sans-serif' }, colorway: ['#36b9cc'], hovermode: 'closest', xaxis: { showgrid: false, tickangle: -45, automargin: true },
            yaxis: { title: 'Disponibilidade %', range: [0, 105], automargin: true },
            margin: { b: 80 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent'
        }

        Plotly.react(corpoChartQuatro, novoTraceChartQuatro, layoutChartQuatro)
        
        if(filtroDinamicoChartQuatro) {
            filtroDinamicoChartQuatro.addEventListener('change', async function(event) {
                if (event.target.classList.contains('filtro-mes')) {
                    const isMarcado = event.target.checked
                    const anoMesSelecionado = event.target.getAttribute('data-ano')
                    const anoDesteMes = filtroDinamicoChartQuatro.querySelector(`.filtro-ano[value="${anoMesSelecionado}"]`)
                    const todosCheckboxes = filtroDinamicoChartQuatro.querySelectorAll('input[type="checkbox"]')
                    
                    let data_inicio = null
                    let data_fim = null
                    
                    if (isMarcado) {
                        anoDesteMes.checked = true
                        const ano = anoDesteMes.value
                        const mes = event.target.value.substring(5,7)
                        
                        data_inicio = `${ano}-${mes}-01`
                        const ultimoDiaMes = new Date(ano, mes, 0).getDate()
                        data_fim = `${ano}-${mes}-${ultimoDiaMes}`
                        
                        const dadosFiltrados = await loadDataDashboard({inicio: data_inicio, fim: data_fim})
                        
                        const nomesElevadores = [...listaElevadores];
                        const valDispFiltrado = listaElevadores.map(nomeElevador => {
                            const achou = dadosFiltrados.ind_quatro.find(item => item.elevador === nomeElevador)
                            return achou ? achou.disponibilidade : 0
                        });
                        const textFormatFilt = valDispFiltrado.map(v => `${v}%`)
                        
                        const dataCustomFilt = listaElevadores.map(nomeElevador => {
                            const achou = dadosFiltrados.ind_quatro.find(item => item.elevador === nomeElevador)
                            if (achou) {
                                return [achou.elevador, achou.tempo_parado, achou.total_mes, achou.dias_uteis, achou.horas_disponiveis]
                            } else {
                                return [nomeElevador, '-', '-', '-', '-']
                            }
                        })
                        
                        const traceFiltrado = [{
                            x: nomesElevadores,
                            y: valDispFiltrado,
                            customdata: dataCustomFilt,
                            type: 'bar',
                            text: textFormatFilt,
                            marker: { color: 'rgba(16, 185, 129, 0.85)', line: { color: '#059669', width: 1 } },
                            hovertemplate: 
                                'Elevador: <b>%{customdata[0]}</b><br><br>' +
                                'Tempo Parado: <b>%{customdata[1]}</b><br>' +
                                'Hrs úteis no Mês Total: <b>%{customdata[2]}</b><br>' +
                                'Dias úteis no Mês Total: <b>%{customdata[3]}</b><br>' +
                                'Horas Disponíveis: <b>%{customdata[4]}</b><br>' +
                                'Disponibilidade: <b>%{y}%</b>' +
                                '<extra></extra>',
                            textposition: 'auto',
                            textfont: { size: 14, weight: 'bold', color: '#1e293b' }
                        }]
                        
                        Plotly.react(corpoChartQuatro, traceFiltrado, layoutChartQuatro)
                        
                        todosCheckboxes.forEach(checkbox => {
                            if (checkbox.checked === false) checkbox.disabled = true;
                        });
                    } else {
                          todosCheckboxes.forEach(checkbox => checkbox.disabled = false);
                          anoDesteMes.checked = false;
                          
                          // Restaura os dados padrão
                          Plotly.react(corpoChartQuatro, novoTraceChartQuatro, layoutChartQuatro)
                      }
                }
            });
        }
    } catch(err) {
        console.error(err);
    }
}

export function atualizarCardsIndicadores() {
    if (!dados_api || Object.keys(dados_api).length === 0) return;

    const widgetInd1Val = document.getElementById('widget-ind1-val');
    if (widgetInd1Val && dados_api.ind_um && dados_api.ind_um.length > 0) {
        const maiorTempo = Math.max(...dados_api.ind_um.map(item => item.min_chegada));
        widgetInd1Val.innerText = `${maiorTempo} min`;
    } else if (widgetInd1Val) {
        widgetInd1Val.innerText = '--';
    }
    
    const widgetInd2Val = document.getElementById('widget-ind2-val');
    if (widgetInd2Val && dados_api.ind_dois) {
        widgetInd2Val.innerText = `${dados_api.ind_dois.length}`;
    } else if (widgetInd2Val) {
        widgetInd2Val.innerText = '--';
    }

    const widgetInd3Val = document.getElementById('widget-ind3-val');
    const widgetInd3Elev = document.getElementById('widget-ind3-elev');
    if (widgetInd3Val && widgetInd3Elev && dados_api.ind_tres && dados_api.ind_tres.length > 0) {
        let elevadorMaisChamados = '--';
        let maxChamados = 0;
        
        dados_api.ind_tres.forEach(serie => {
            if (serie.y && serie.y.length > 0) {
                const chamadosTotais = serie.y.reduce((acc, curr) => acc + curr, 0);
                if (chamadosTotais > maxChamados) {
                    maxChamados = chamadosTotais;
                    elevadorMaisChamados = serie.name;
                }
            }
        });

        if (maxChamados > 0) {
            widgetInd3Val.innerText = maxChamados;
            widgetInd3Elev.innerText = elevadorMaisChamados;
        } else {
            widgetInd3Val.innerText = '--';
            widgetInd3Elev.innerText = '--';
        }
    }

    const widgetInd4Val = document.getElementById('widget-ind4-val');
    const widgetInd4Elev = document.getElementById('widget-ind4-elev');
    if (widgetInd4Val && widgetInd4Elev && dados_api.ind_quatro && dados_api.ind_quatro.length > 0) {
        let elevadorMenorDisp = '--';
        let menorDisp = 100;
        let achouAlgum = false;
        
        dados_api.ind_quatro.forEach(item => {
            if (item.disponibilidade < menorDisp) {
                menorDisp = item.disponibilidade;
                elevadorMenorDisp = item.elevador;
                achouAlgum = true;
            }
        });
        
        if (achouAlgum) {
            widgetInd4Val.innerText = `${menorDisp}%`;
            widgetInd4Elev.innerText = elevadorMenorDisp;
        } else {
            widgetInd4Val.innerText = '100%';
            widgetInd4Elev.innerText = '--';
        }
    }
}

let intervalId = null;

async function initStatusElevadores() {
    await fetchAndRenderStatus();
    if (intervalId) clearInterval(intervalId);
    intervalId = setInterval(updateTimers, 1000);
    
    // Atualizar os dados a cada 30 segundos
    setInterval(fetchAndRenderStatus, 30000);
}

async function fetchAndRenderStatus() {
    const grid = document.getElementById('status-elevadores-grid');
    if (!grid) return;
    
    try {
        const resp = await fetch('/elevadores/api/elevadoress/status_elevadores/');
        const data = await resp.json();
        const elevadores = data.status_elevadores || [];
        
        let htmlCards = '';
        elevadores.forEach(elev => {
            const isParado = elev.status === 'PARADO';
            const isProgramado = elev.status === 'PROGRAMADO';
            
            let iconClass = 'bi-check-circle-fill';
            let cardClass = 'ativo';
            let badgeClass = 'bg-success';
            
            if (isParado) {
                iconClass = 'bi-exclamation-triangle-fill';
                cardClass = 'parado';
                badgeClass = 'bg-danger';
            } else if (isProgramado) {
                iconClass = 'bi-calendar-event-fill';
                cardClass = 'programado';
                badgeClass = 'bg-primary';
            }
            
            let timerHtml = '';
            if (isParado && elev.data_hora_abertura) {
                timerHtml = `<div class="elev-timer" data-start="${elev.data_hora_abertura}">Calculando...</div>`;
            }
            
            let progHtml = '';
            if (isProgramado && elev.programacao) {
                let motivoHtml = elev.motivo ? `<br><span class="text-secondary fw-normal">Motivo: ${elev.motivo}</span>` : '';
                progHtml = `<div class="mt-2 text-primary fw-bold" style="font-size: 0.75rem;">
                                ${elev.programacao}
                                ${motivoHtml}
                            </div>`;
            }
            
            // Note: Usamos data- attributes para evitar erros de sintaxe com aspas no onclick
            htmlCards += `
                <div class="elev-card ${cardClass} clickable-elev-card" style="cursor: pointer;" 
                     data-elevador="${elev.elevador}" 
                     data-status="${elev.status}" 
                     data-programacao="${elev.programacao || ''}"
                     data-motivo="${elev.motivo || ''}">
                    <i class="bi ${iconClass} elev-icon"></i>
                    <h6 class="mb-1 fw-bold">${elev.elevador}</h6>
                    <span class="badge ${badgeClass} text-uppercase" style="font-size:0.7rem;">${elev.status}</span>
                    ${timerHtml}
                    ${progHtml}
                </div>
            `;
        });
        
        grid.innerHTML = htmlCards;
        updateTimers();
        
        // Attach click listeners
        document.querySelectorAll('.clickable-elev-card').forEach(card => {
            card.addEventListener('click', function() {
                openStatusModal(this.dataset.elevador, this.dataset.status, this.dataset.programacao, this.dataset.motivo);
            });
        });
    } catch(err) {
        console.error("Erro ao carregar status dos elevadores", err);
        grid.innerHTML = '<div class="text-danger">Erro ao carregar status</div>';
    }
}

function updateTimers() {
    const timers = document.querySelectorAll('.elev-timer');
    const now = new Date();
    
    timers.forEach(timer => {
        const startStr = timer.getAttribute('data-start');
        if (!startStr) return;
        
        const start = new Date(startStr);
        const diffMs = now - start;
        
        if (diffMs < 0) return;
        
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        const diffHrs = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
        const diffSecs = Math.floor((diffMs % (1000 * 60)) / 1000);
        
        let timeStr = [];
        if (diffDays > 0) timeStr.push(`${diffDays}d`);
        if (diffHrs > 0 || diffDays > 0) timeStr.push(`${diffHrs}h`);
        if (diffMins > 0 || diffHrs > 0 || diffDays > 0) timeStr.push(`${diffMins}m`);
        timeStr.push(`${diffSecs}s`);
        
        timer.innerText = timeStr.join(' ');
    });
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

function openStatusModal(elevador, statusAtual, programacaoAtual, motivoAtual) {
    document.getElementById('status-elevador-nome').value = elevador;
    document.getElementById('display-elevador-nome').value = elevador;
    document.getElementById('status-elevador-select').value = statusAtual;
    
    const divProg = document.getElementById('div-programacao');
    const inputProg = document.getElementById('status-elevador-programacao');
    const inputMotivo = document.getElementById('status-elevador-motivo');
    
    if (statusAtual === 'PROGRAMADO') {
        divProg.style.display = 'block';
        inputProg.value = programacaoAtual;
        inputProg.required = true;
        if(inputMotivo) {
            inputMotivo.value = motivoAtual || '';
            inputMotivo.required = true;
        }
    } else {
        divProg.style.display = 'none';
        inputProg.value = '';
        inputProg.required = false;
        if(inputMotivo) {
            inputMotivo.value = '';
            inputMotivo.required = false;
        }
    }
    
    const modal = new bootstrap.Modal(document.getElementById('modal-status-elevador'));
    modal.show();
}

document.addEventListener('DOMContentLoaded', () => {
    const graficosTab = document.getElementById('graficos-tab');
    if (graficosTab) {
        graficosTab.addEventListener('shown.bs.tab', function () {
            document.querySelectorAll('.js-plotly-plot').forEach(el => {
                Plotly.Plots.resize(el);
            });
        });
    }

    const statusSelect = document.getElementById('status-elevador-select');
    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            const divProg = document.getElementById('div-programacao');
            const inputProg = document.getElementById('status-elevador-programacao');
            const inputMotivo = document.getElementById('status-elevador-motivo');
            const inputProgInicio = document.getElementById('status-elevador-prog-inicio');
            const inputProgFim = document.getElementById('status-elevador-prog-fim');
            
            const divParada = document.getElementById('div-parada');
            const inputDataParada = document.getElementById('status-elevador-data-parada');

            if (this.value === 'PROGRAMADO') {
                divProg.style.display = 'block';
                inputProg.required = true;
                if(inputMotivo) inputMotivo.required = true;
                if(inputProgInicio) inputProgInicio.required = true;
                if(inputProgFim) inputProgFim.required = true;
                
                divParada.style.display = 'none';
                if(inputDataParada) inputDataParada.required = false;
            } else if (this.value === 'PARADO') {
                divProg.style.display = 'none';
                inputProg.required = false;
                inputProg.value = '';
                if(inputMotivo) {
                    inputMotivo.required = false;
                    inputMotivo.value = '';
                }
                if(inputProgInicio) {
                    inputProgInicio.required = false;
                    inputProgInicio.value = '';
                }
                if(inputProgFim) {
                    inputProgFim.required = false;
                    inputProgFim.value = '';
                }
                
                divParada.style.display = 'block';
                if(inputDataParada) {
                    inputDataParada.required = true;
                    // preencher com data atual
                    const now = new Date();
                    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
                    inputDataParada.value = now.toISOString().slice(0,16);
                }
            } else {
                divProg.style.display = 'none';
                inputProg.required = false;
                inputProg.value = '';
                if(inputMotivo) {
                    inputMotivo.required = false;
                    inputMotivo.value = '';
                }
                if(inputProgInicio) {
                    inputProgInicio.required = false;
                    inputProgInicio.value = '';
                }
                if(inputProgFim) {
                    inputProgFim.required = false;
                    inputProgFim.value = '';
                }
                
                divParada.style.display = 'none';
                if(inputDataParada) {
                    inputDataParada.required = false;
                    inputDataParada.value = '';
                }
            }
        });
    }

    const formStatus = document.getElementById('form-status-elevador');
    if (formStatus) {
        formStatus.addEventListener('submit', async function(e) {
            e.preventDefault();
            const elevador = document.getElementById('status-elevador-nome').value;
            const status = document.getElementById('status-elevador-select').value;
            const programacao = document.getElementById('status-elevador-programacao').value;
            const motivoEl = document.getElementById('status-elevador-motivo');
            const motivo = motivoEl ? motivoEl.value : '';
            
            const progInicioEl = document.getElementById('status-elevador-prog-inicio');
            const programacao_inicio = progInicioEl ? progInicioEl.value : '';
            const progFimEl = document.getElementById('status-elevador-prog-fim');
            const programacao_fim = progFimEl ? progFimEl.value : '';
            
            const dataParadaEl = document.getElementById('status-elevador-data-parada');
            const data_hora_parada = dataParadaEl ? dataParadaEl.value : '';

            try {
                const response = await fetch('/elevadores/api/elevadoress/status_elevadores/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ elevador, status, programacao, motivo, data_hora_parada, programacao_inicio, programacao_fim })
                });

                if (response.ok) {
                    const modalEl = document.getElementById('modal-status-elevador');
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    modal.hide();
                    fetchAndRenderStatus(); // recarrega a grid
                } else {
                    const data = await response.json();
                    alert("Erro ao atualizar status: " + (data.error || 'Erro desconhecido.'));
                }
            } catch (err) {
                console.error(err);
                alert("Erro ao tentar atualizar o status.");
            }
        });
    }
});

async function dadosIndicadorDois() {
    const filtroDinamicoChartDois = document.getElementById('filtro-dinamico-chart-2');
    const corpoChartDois = document.getElementById('chart-2');
    
    if(!corpoChartDois) return;
    
    try {
        if(filtroDinamicoChartDois) {
            filtroAnosMeses(filtroDinamicoChartDois, rangeDeAnos, rangeDeMeses);
        }
        
        const x_days = [];
        const y_elevs = [];
        const text_status = [];
        const colors = [];
        const custom_data = [];
        
        if(dados_api.ind_dois) {
            dados_api.ind_dois.forEach(item => {
                if(item.status === 'PARADO') {
                    x_days.push(0);
                    y_elevs.push(item.elevador);
                    text_status.push(item.status);
                    colors.push('#6c757d');
                    custom_data.push(['-', '-']);
                } else if(item.data_execucao) {
                    const parts = item.data_execucao.split('/'); // DD/MM/YYYY
                    if(parts.length === 3) {
                        x_days.push(parseInt(parts[0], 10)); // Day of month
                        y_elevs.push(item.elevador);
                        text_status.push(item.status);
                        colors.push(item.status === 'EXECUTADO' ? '#10b981' : (item.status === 'INOPERANTE' ? '#ef4444' : '#f59e0b'));
                        custom_data.push([item.ordem_servico, item.tecnico]);
                    }
                }
            });
        }
        
        const trace = {
            x: x_days,
            y: y_elevs,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: colors,
                line: { width: 1, color: 'white' }
            },
            customdata: custom_data,
            text: text_status,
            hovertemplate: 
                '<b>Elevador:</b> %{y}<br>' +
                '<b>Dia Execução:</b> %{x}<br>' +
                '<b>Status:</b> %{text}<br>' +
                '<b>OS:</b> %{customdata[0]}<br>' +
                '<b>Técnico:</b> %{customdata[1]}' +
                '<extra></extra>'
        };

        const anoAtual = parseInt(inicioMesAtual.substring(0, 4));
        const mesAtual = parseInt(inicioMesAtual.substring(5, 7));
        const ultimoDiaAtual = new Date(anoAtual, mesAtual, 0).getDate();

        const tickvalsAtual = [];
        const ticktextAtual = [];
        for (let i = 1; i <= ultimoDiaAtual; i++) {
            tickvalsAtual.push(i);
            ticktextAtual.push(`${i.toString().padStart(2, '0')}/${mesAtual.toString().padStart(2, '0')}`);
        }

        const layoutChartDois = { margin: { l: 40, r: 20, t: 30, b: 40 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { family: 'Inter, sans-serif' }, colorway: ['#1cc88a'], hovermode: 'closest', xaxis: { showgrid: false,
                title: 'Dia do Mês',
                range: [0, ultimoDiaAtual],
                tickmode: 'array',
                tickvals: tickvalsAtual,
                ticktext: ticktextAtual,
                tickangle: -45
            },
            yaxis: {
                type: 'category',
                automargin: true,
            },
            height: 500,
            margin: { l: 150, r: 20, t: 30, b: 50 },
            plot_bgcolor: 'transparent',
            shapes: [
                {
                    type: 'line',
                    x0: 10,
                    x1: 10,
                    y0: 0,
                    y1: 1,
                    yref: 'paper',
                    line: {
                        color: 'red',
                        width: 2,
                        dash: 'dashdot'
                    }
                }
            ]
        };

        let ultimaDataStr = '--';
        if (x_days.length > 0) {
            const maxDay = Math.max(...x_days);
            ultimaDataStr = `Dia ${maxDay.toString().padStart(2, '0')}/${mesAtual.toString().padStart(2, '0')}`;
        }
        const widgetInd2Val = document.getElementById('widget-ind2-val');
        if (widgetInd2Val) {
            widgetInd2Val.innerText = ultimaDataStr;
        }

        Plotly.react(corpoChartDois, [trace], layoutChartDois);

        if(filtroDinamicoChartDois) {
            filtroDinamicoChartDois.addEventListener('change', async function(event) {
                if (event.target.classList.contains('filtro-mes')) {
                    const isMarcado = event.target.checked;
                    const anoMesSelecionado = event.target.getAttribute('data-ano');
                    const anoDesteMes = filtroDinamicoChartDois.querySelector(`.filtro-ano[value="${anoMesSelecionado}"]`);
                    const todosCheckboxes = filtroDinamicoChartDois.querySelectorAll('input[type="checkbox"]');
            
                    let data_inicio = null;
                    let data_fim = null;

                    if (isMarcado) {
                        anoDesteMes.checked = true;
                        const ano = anoDesteMes.value;
                        const mes = event.target.value.substring(5,7);
            
                        data_inicio = `${ano}-${mes}-01`;
                        const ultimoDiaMes = new Date(ano, mes, 0).getDate();
                        data_fim = `${ano}-${mes}-${ultimoDiaMes}`;
    
                        const dadosFiltrados = await loadDataDashboard({inicio: data_inicio, fim: data_fim});
                        
                        const novoX = [];
                        const novoY = [];
                        const novoText = [];
                        const novaColor = [];
                        const novoCustom = [];
                        
                        if(dadosFiltrados.ind_dois) {
                            dadosFiltrados.ind_dois.forEach(item => {
                                if(item.status === 'PARADO') {
                                    novoX.push(0);
                                    novoY.push(item.elevador);
                                    novoText.push(item.status);
                                    novaColor.push('#6c757d');
                                    novoCustom.push(['-', '-']);
                                } else if(item.data_execucao) {
                                    const parts = item.data_execucao.split('/');
                                    if(parts.length === 3) {
                                        novoX.push(parseInt(parts[0], 10));
                                        novoY.push(item.elevador);
                                        novoText.push(item.status);
                                        novaColor.push(item.status === 'EXECUTADO' ? '#10b981' : (item.status === 'INOPERANTE' ? '#ef4444' : '#f59e0b'));
                                        novoCustom.push([item.ordem_servico, item.tecnico]);
                                    }
                                }
                            });
                        }
                        
                        const novoTrace = [{
                            ...trace,
                            x: novoX,
                            y: novoY,
                            text: novoText,
                            marker: { ...trace.marker, color: novaColor },
                            customdata: novoCustom
                        }];

                        let ultimaDataFiltradaStr = '--';
                        if (novoX.length > 0) {
                            const maxDayFiltro = Math.max(...novoX);
                            ultimaDataFiltradaStr = `Dia ${maxDayFiltro.toString().padStart(2, '0')}/${mes.toString().padStart(2, '0')}`;
                        }
                        if (widgetInd2Val) {
                            widgetInd2Val.innerText = ultimaDataFiltradaStr;
                        }
                        
                        const tickvalsFiltro = [];
                        const ticktextFiltro = [];
                        for (let i = 1; i <= ultimoDiaMes; i++) {
                            tickvalsFiltro.push(i);
                            ticktextFiltro.push(`${i.toString().padStart(2, '0')}/${mes.toString().padStart(2, '0')}`);
                        }

                        // Atualiza a janela de visualização do gráfico (range) para o mês filtrado
                        layoutChartDois.xaxis.range = [0, ultimoDiaMes];
                        layoutChartDois.xaxis.tickvals = tickvalsFiltro;
                        layoutChartDois.xaxis.ticktext = ticktextFiltro;
                        layoutChartDois.shapes[0].x0 = 10;
                        layoutChartDois.shapes[0].x1 = 10;
            
                        Plotly.react(corpoChartDois, novoTrace, layoutChartDois);
            
                        todosCheckboxes.forEach(checkbox => {
                            if (checkbox.checked === false) checkbox.disabled = true;
                        });
                    } else {
                        todosCheckboxes.forEach(checkbox => checkbox.disabled = false);
                        anoDesteMes.checked = false;
                        
                        if (widgetInd2Val) {
                            widgetInd2Val.innerText = ultimaDataStr;
                        }

                        // Restaura os dados padrão
                        layoutChartDois.xaxis.range = [0, ultimoDiaAtual];
                        layoutChartDois.xaxis.tickvals = tickvalsAtual;
                        layoutChartDois.xaxis.ticktext = ticktextAtual;
                        layoutChartDois.shapes[0].x0 = 10;
                        layoutChartDois.shapes[0].x1 = 10;
                        Plotly.react(corpoChartDois, [trace], layoutChartDois);
                    }
                }
            });
        }
    } catch(erro) {
        console.error("Erro ao renderizar gráfico 2:", erro);
        corpoChartDois.innerHTML = '<div class="alert alert-danger m-3">Falha ao carregar gráfico.</div>';
    }
}
    }
}

// ==========================================
// CENTRAL DE DEMANDAS PENDENTES (UNIFICADO)
// ==========================================

window.carregarWidgetDemandasDashboard = async function() {
    try {
        const [resOs, resPecas, resMpm] = await Promise.all([
            fetch('/elevadores/api/elevadoress/'),
            fetch('/elevadores/api/peca_manutencao/'),
            fetch('/elevadores/api/manutencao_preventiva/')
        ]);

        let demandas = [];

        if (resOs.ok) {
            const osData = await resOs.json();
            osData.filter(o => o.status !== 'CONCLUIDA' && o.status !== 'CONCLUÍDA').forEach(o => {
                let tempo = o.min_chegada ? `${o.min_chegada} min` : 'Calculando...';
                if (!o.min_chegada && (o.status === 'ABERTA' || o.status === 'EM ANDAMENTO')) {
                    const minPassados = Math.floor((new Date() - new Date(o.data_hora)) / 60000);
                    tempo = `${minPassados} min`;
                } else if (o.status === 'AGUARDANDO PEÇAS') {
                    tempo = 'Pausado';
                }
                demandas.push({
                    tipo: 'os',
                    dataOrigem: o.data_hora,
                    dataExibicao: new Date(o.data_hora).toLocaleDateString('pt-BR'),
                    ref: o.protocolo,
                    tipoNome: o.status === 'ABERTA' ? '<span class="badge bg-secondary">OS Aberta</span>' : '<span class="badge bg-primary">Em Andamento</span>',
                    equip: o.elevador,
                    tempo: tempo,
                    status: o.status,
                    extra: o
                });
            });
        }

        if (resPecas.ok) {
            const pecasData = await resPecas.json();
            pecasData.filter(p => p.status !== 'SUBSTITUIDA').forEach(p => {
                demandas.push({
                    tipo: 'peca',
                    dataOrigem: p.data_registro || p.created_at || new Date().toISOString(),
                    dataExibicao: p.data_registro ? p.data_registro.split('-').reverse().join('/') : '-',
                    ref: p.tipo_peca,
                    tipoNome: '<span class="badge bg-warning text-dark">Peça</span>',
                    equip: p.elevador,
                    tempo: p.status
                });
            });
        }

        if (resMpm.ok) {
            const mpmData = await resMpm.json();
            mpmData.filter(m => m.status === 'NAO_EXECUTADO').forEach(m => {
                demandas.push({
                    tipo: 'mpm',
                    dataOrigem: m.mes_referencia,
                    dataExibicao: m.mes_referencia,
                    ref: 'Prevenção Mensal',
                    tipoNome: '<span class="badge bg-danger">MPM Atrasada</span>',
                    equip: m.elevador,
                    tempo: 'Atrasada'
                });
            });
        }

        // Ordenar demandas: OS no topo (mais nova para mais antiga), demais da mais antiga para mais nova
        demandas.sort((a, b) => {
            if (a.tipo === 'os' && b.tipo !== 'os') return -1;
            if (a.tipo !== 'os' && b.tipo === 'os') return 1;
            if (a.tipo === 'os' && b.tipo === 'os') {
                return new Date(b.dataOrigem) - new Date(a.dataOrigem);
            }
            return new Date(a.dataOrigem) - new Date(b.dataOrigem);
        });

        const listGroup = document.getElementById('lista-demandas-dashboard');
        if (listGroup) {
            listGroup.innerHTML = '';
            if (demandas.length === 0) {
                listGroup.innerHTML = '<div class="text-center text-success py-3 fw-bold"><i class="bi bi-emoji-smile fs-4 d-block mb-1"></i>Tudo em Dia! Nenhuma pendência.</div>';
            } else {
                demandas.slice(0, 3).forEach(d => {
                    listGroup.innerHTML += `
                        <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center border-0 px-2 rounded mb-1" style="background-color: #fffaf0;">
                            <div>
                                <small class="text-danger"><i class="bi bi-clock me-1"></i> Data/Ref: ${d.dataExibicao}</small><br>
                                <span class="fw-bold text-dark fs-6">${d.ref}</span> ${d.tipoNome}<br>
                                <small class="text-muted">Equip: ${d.equip}</small>
                            </div>
                            <i class="bi bi-chevron-right text-danger"></i>
                        </div>
                    `;
                });
            }
        }

        const badge = document.getElementById('badge-demandas-pendentes');
        if (badge) badge.innerText = demandas.length;

    } catch(e) {
        console.error("Erro no widget de demandas", e);
    }
}

// Chamar no carregamento
document.addEventListener('DOMContentLoaded', () => {
    carregarWidgetDemandasDashboard();
});

window.abrirModalDemandasPendentes = async function() {
    try {
        const [resOs, resPecas, resMpm] = await Promise.all([
            fetch('/elevadores/api/elevadoress/'),
            fetch('/elevadores/api/peca_manutencao/'),
            fetch('/elevadores/api/manutencao_preventiva/')
        ]);

        let demandas = [];

        if (resOs.ok) {
            const osData = await resOs.json();
            osData.filter(o => o.status !== 'CONCLUIDA' && o.status !== 'CONCLUÍDA').forEach(o => {
                let tempo = o.min_chegada ? `${o.min_chegada} min` : 'Calculando...';
                if (!o.min_chegada && (o.status === 'ABERTA' || o.status === 'EM ANDAMENTO')) {
                    const minPassados = Math.floor((new Date() - new Date(o.data_hora)) / 60000);
                    tempo = `${minPassados} min`;
                } else if (o.status === 'AGUARDANDO PEÇAS') {
                    tempo = 'Pausado';
                }
                demandas.push({
                    tipo: 'os',
                    dataOrigem: o.data_hora,
                    dataExibicao: new Date(o.data_hora).toLocaleDateString('pt-BR'),
                    ref: o.protocolo,
                    tipoNome: o.status === 'ABERTA' ? '<span class="badge bg-secondary">OS Aberta</span>' : '<span class="badge bg-primary">Em Andamento</span>',
                    equip: o.elevador,
                    tempo: tempo,
                    id: o.id,
                    status: o.status,
                    extra: o
                });
            });
        }

        if (resPecas.ok) {
            const pecasData = await resPecas.json();
            pecasData.filter(p => p.status !== 'SUBSTITUIDA').forEach(p => {
                demandas.push({
                    tipo: 'peca',
                    dataOrigem: p.data_registro || p.created_at || new Date().toISOString(),
                    dataExibicao: p.data_registro ? p.data_registro.split('-').reverse().join('/') : '-',
                    ref: p.tipo_peca,
                    tipoNome: '<span class="badge bg-warning text-dark">Peça</span>',
                    equip: p.elevador,
                    tempo: p.status,
                    id: p.id,
                    extra: p
                });
            });
        }

        if (resMpm.ok) {
            const mpmData = await resMpm.json();
            mpmData.filter(m => m.status === 'NAO_EXECUTADO').forEach(m => {
                demandas.push({
                    tipo: 'mpm',
                    dataOrigem: m.mes_referencia,
                    dataExibicao: m.mes_referencia,
                    ref: 'Prevenção Mensal',
                    tipoNome: '<span class="badge bg-danger">MPM Atrasada</span>',
                    equip: m.elevador,
                    tempo: 'Atrasada',
                    id: m.id,
                    extra: m
                });
            });
        }

        // Ordenar demandas: OS no topo (mais nova para mais antiga), demais da mais antiga para mais nova
        demandas.sort((a, b) => {
            if (a.tipo === 'os' && b.tipo !== 'os') return -1;
            if (a.tipo !== 'os' && b.tipo === 'os') return 1;
            if (a.tipo === 'os' && b.tipo === 'os') {
                return new Date(b.dataOrigem) - new Date(a.dataOrigem);
            }
            return new Date(a.dataOrigem) - new Date(b.dataOrigem);
        });

        const tbody = document.getElementById('demandas-tbody');
        tbody.innerHTML = '';

        if (demandas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-success py-4"><i class="bi bi-emoji-smile fs-4 d-block mb-2"></i>Nenhuma pendência encontrada!</td></tr>';
        } else {
            demandas.forEach(d => {
                let btnAction = '';
                if (d.tipo === 'os') {
                    if (d.status === 'ABERTA') {
                        const osStr = encodeURIComponent(JSON.stringify(d.extra));
                        btnAction = `<button class="btn btn-sm btn-primary fw-bold shadow-sm" data-bs-dismiss="modal" onclick="setTimeout(() => abrirModalRegistrarChegada('${osStr}'), 400)"><i class="bi bi-person-walking me-1"></i>Registrar Chegada</button>`;
                    } else {
                        btnAction = `<button class="btn btn-sm btn-success fw-bold shadow-sm" data-bs-dismiss="modal" onclick="setTimeout(() => abrirConclusaoOSDemandas(${d.id}), 400)"><i class="bi bi-check2-circle me-1"></i>Concluir O.S.</button>`;
                    }
                } else if (d.tipo === 'peca') {
                    const pecaStr = encodeURIComponent(JSON.stringify(d.extra));
                    btnAction = `
                        <div class="d-flex flex-nowrap gap-1">
                            <button class="btn btn-sm btn-outline-primary" style="white-space: nowrap;" data-bs-dismiss="modal" onclick="setTimeout(() => abrirVisualizarPeca('${pecaStr}'), 400)" title="Visualizar Peça">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-warning text-dark fw-bold shadow-sm" data-bs-dismiss="modal" onclick="setTimeout(() => abrirConclusaoPecaDemandas(${d.id}), 400)"><i class="bi bi-tools me-1"></i>Trocar Peça</button>
                        </div>
                    `;
                } else if (d.tipo === 'mpm') {
                    const mpmStr = encodeURIComponent(JSON.stringify(d.extra));
                    const mpmConcluirStr = encodeURIComponent(JSON.stringify({id: d.id, elevador: d.equip, mes: d.dataExibicao}));
                    btnAction = `
                        <div class="d-flex flex-nowrap gap-1">
                            <button class="btn btn-sm btn-outline-primary" style="white-space: nowrap;" data-bs-dismiss="modal" onclick="setTimeout(() => abrirVisualizarMPM('${mpmStr}'), 400)" title="Visualizar MPM">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-danger fw-bold shadow-sm" data-bs-dismiss="modal" onclick="setTimeout(() => abrirConclusaoMPMDemandas('${mpmConcluirStr}'), 400)"><i class="bi bi-calendar-check me-1"></i>Executar MPM</button>
                        </div>
                    `;
                }

                tbody.innerHTML += `
                    <tr>
                        <td class="text-muted fw-bold">${d.dataExibicao}</td>
                        <td class="fw-bold">${d.ref}</td>
                        <td>${d.tipoNome}</td>
                        <td>${d.equip}</td>
                        <td class="text-danger fw-bold">${d.tempo}</td>
                        <td>${btnAction}</td>
                    </tr>
                `;
            });
        }

        const badge = document.getElementById('badge-demandas-pendentes');
        if (badge) badge.innerText = demandas.length;

        const modalEl = document.getElementById('modal-lista-concluir-demandas');
        // Garantimos que não existam múltiplos backdrops usando getInstance
        let modal = bootstrap.Modal.getInstance(modalEl);
        if (!modal) {
            modal = new bootstrap.Modal(modalEl);
        }
        modal.show();
        openConcluirModal(id);
    } else {
        console.error('openConcluirModal não definida');
    }
}

window.abrirConclusaoMPMDemandas = function(mpmStrEncoded) {
    const data = JSON.parse(decodeURIComponent(mpmStrEncoded));
        document.getElementById('concluirMPMId').value = data.id;
        document.getElementById('concluirMPMElevadorText').innerText = data.elevador;
        document.getElementById('concluirMPMMesText').innerText = data.mes;
        document.getElementById('concluirMPMStatus').value = 'EXECUTADO';
        document.getElementById('concluirMPMData').value = new Date().toISOString().split('T')[0];
        
        const userField = document.getElementById('user_hidden_logado');
        if(userField) document.getElementById('concluirMPMTecnico').value = userField.value;

        const modalEl = document.getElementById('modalConcluirMPM');
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
}

document.getElementById('formConcluirMPM')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    const id = document.getElementById('concluirMPMId').value;
    const tec = document.getElementById('concluirMPMTecnico').value;
    const dataExec = document.getElementById('concluirMPMData').value;
    const status = document.getElementById('concluirMPMStatus').value;
    
    // Obter CSRF token
    let csrfToken = '';
    const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if(csrfElement) csrfToken = csrfElement.value;
    else {
        // Tentar obter via cookie se não houver no dom
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                csrfToken = cookie.substring('csrftoken='.length, cookie.length);
                break;
            }
        }
    }

    try {
        const resp = await fetch('/elevadores/api/manutencao_preventiva/' + id + '/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                tecnico: tec,
                data_execucao: dataExec,
                status: status
            })
        });

        if(resp.ok) {
            Swal.fire('Sucesso', 'Manutenção registrada!', 'success');
            const mEl = document.getElementById('modalConcluirMPM');
            if (mEl) {
                const m = bootstrap.Modal.getInstance(mEl);
                if(m) m.hide();
            }
            abrirModalDemandasPendentes();
            if(typeof loadMPMTable === 'function') loadMPMTable();
            window.location.reload();
        } else {
            Swal.fire('Erro', 'Não foi possível salvar', 'error');
        }
    } catch(err) {
        console.error(err);
        Swal.fire('Erro', 'Erro de conexão', 'error');
    }
});

window.abrirModalRegistrarChegada = function(osStrEncoded) {
    const data = JSON.parse(decodeURIComponent(osStrEncoded));
    document.getElementById('chegadaIdOS').value = data.id;
    
    // Preencher campos read-only com informações da abertura
    const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
    
    setVal('chegadaProtocolo', data.protocolo || '');
    setVal('chegadaElevador', data.elevador || '');
    
    let dataAbertura = '';
    if(data.data_hora) {
        dataAbertura = new Date(data.data_hora).toLocaleString('pt-BR');
    }
    setVal('chegadaDataAbertura', dataAbertura);
    
    setVal('chegadaAprisionamento', (data.aprisionamento === true || data.aprisionamento === 'Sim') ? 'Sim' : 'Não');
    setVal('chegadaElevadorParado', data.elevador_parado || 'ATIVO');
    setVal('chegadaAtendente', data.atendente || '');
    setVal('chegadaSolicitante', data.solicitante || '');
    setVal('chegadaAlarmeEms', data.alarme_ems || 'Nenhum');
    setVal('chegadaOcorrencia', data.ocorrencia || '');
    
    // Configurar horário atual padrão
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    setVal('chegadaDataHora', now.toISOString().slice(0, 16));
    
    // Obter registrante
    const userField = document.getElementById('user_hidden_logado');
    if(userField) setVal('chegadaRegistrador', userField.value);
    
    setVal('chegadaProtocolo', data.protocolo || '');
    setVal('chegadaElevador', data.elevador || '');
    
    let dataAbertura = '';
    if(data.data_hora) {
        dataAbertura = new Date(data.data_hora).toLocaleString('pt-BR');
    }
    setVal('chegadaDataAbertura', dataAbertura);
    
    setVal('chegadaAprisionamento', (data.aprisionamento === true || data.aprisionamento === 'Sim') ? 'Sim' : 'Não');
    setVal('chegadaElevadorParado', data.elevador_parado || 'ATIVO');
    setVal('chegadaAtendente', data.atendente || '');
    setVal('chegadaSolicitante', data.solicitante || '');
    setVal('chegadaAlarmeEms', data.alarme_ems || 'Nenhum');
    setVal('chegadaOcorrencia', data.ocorrencia || '');
    
    // Configurar horário atual padrão
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    setVal('chegadaDataHora', now.toISOString().slice(0, 16));
    
    // Obter registrante
    const userField = document.getElementById('user_hidden_logado');
    if(userField) setVal('chegadaRegistrador', userField.value);

    setVal('chegadaTecnico', '');
    setVal('chegadaAcompanhante', '');

    // Inicializa Select2 no campo chegadaTecnico
    const $selectTecnico = $('#chegadaTecnico');
    if (!$selectTecnico.hasClass("select2-hidden-accessible")) {
        $selectTecnico.select2({
            theme: 'bootstrap-5',
            dropdownParent: $('#modalRegistrarChegadaOS'),
            tags: true,
            placeholder: "Ex: João Silva ou selecione na lista",
            allowClear: true
        });
    }

    // Inicializa Select2 no campo chegadaAcompanhante
    const $selectAcompanhante = $('#chegadaAcompanhante');
    if (!$selectAcompanhante.hasClass("select2-hidden-accessible")) {
        $selectAcompanhante.select2({
            theme: 'bootstrap-5',
            dropdownParent: $('#modalRegistrarChegadaOS'),
            tags: true,
            placeholder: "Selecione o técnico do TSE",
            allowClear: true
        });
    }

    // Buscar técnicos da Otis e preencher selects (chegadaTecnico usa Select2, os demais são selects normais)
    if (window.tecnicosOtisCache) {
        preencherSelectsTecnicos(window.tecnicosOtisCache);
    } else {
        fetch('/elevadores/api/elevadoress/tecnicos_otis/')
            .then(res => res.json())
            .then(tecnicos => {
                window.tecnicosOtisCache = tecnicos;
                preencherSelectsTecnicos(tecnicos);
            })
            .catch(err => console.error('Erro ao buscar técnicos da Otis', err));
    }

    function preencherSelectsTecnicos(tecnicos) {
        // 1. Select2 para chegadaTecnico
        $selectTecnico.empty();
        $selectTecnico.append(new Option('', '', false, false)); // placeholder
        tecnicos.forEach(tec => {
            $selectTecnico.append(new Option(tec, tec, false, false));
        });
        $selectTecnico.val(null).trigger('change');
    }

    // Buscar equipe do TSE (Contrato de Manutenção Predial) e preencher select2
    fetch('/empresas/api/contatos_por_app/?app=MANUTENCAO_PREDIAL')
        .then(res => res.json())
        .then(contatos => {
            $selectAcompanhante.empty();
            $selectAcompanhante.append(new Option('', '', false, false)); // placeholder
            contatos.forEach(c => {
                const cargoStr = (c.cargo || '').toLowerCase();
                if (cargoStr.includes('técnico') || cargoStr.includes('tecnico') || cargoStr.includes('supervisor')) {
                    const valueStr = `${c.nome} (${c.cargo})`;
                    const textStr = `${c.nome} - ${c.cargo} - ${c.empresa}`;
                    $selectAcompanhante.append(new Option(textStr, valueStr, false, false));
                }
            });

            const loggedUser = document.getElementById('chegadaAcompanhante').getAttribute('data-logged-user');
            if (loggedUser) {
                let optionsArray = $selectAcompanhante.find('option').toArray();
                let optionExists = optionsArray.some(opt => opt.value.startsWith(loggedUser));
                
                if (!optionExists) {
                    const valueStr = `${loggedUser} (Usuário Sesen)`;
                    const textStr = `${loggedUser} - Usuário Sesen`;
                    $selectAcompanhante.append(new Option(textStr, valueStr, false, false));
                }
                
                let optionToSelect = $selectAcompanhante.find('option').toArray().find(opt => opt.value.startsWith(loggedUser));
                if (optionToSelect) {
                    $selectAcompanhante.val(optionToSelect.value).trigger('change');
                } else {
                    $selectAcompanhante.val(null).trigger('change');
                }
            } else {
                $selectAcompanhante.val(null).trigger('change');
            }
        })
        .catch(err => console.error('Erro ao buscar equipe da manutenção predial', err));

    const modalEl = document.getElementById('modalRegistrarChegadaOS');
    if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
}

document.getElementById('formRegistrarChegadaOS')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    const id = document.getElementById('chegadaIdOS').value;
    const dataChegada = document.getElementById('chegadaDataHora').value;
    const tec = document.getElementById('chegadaTecnico').value;
    const acomp = document.getElementById('chegadaAcompanhante').value;
    const registrador = document.getElementById('chegadaRegistrador').value;

    let csrfToken = '';
    const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if(csrfElement) csrfToken = csrfElement.value;
    else {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                csrfToken = cookie.substring('csrftoken='.length, cookie.length);
                break;
            }
        }
    }

    try {
        const resp = await fetch(`/elevadores/api/elevadoress/${id}/registrar_chegada/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                data_hora_chegada: dataChegada,
                tecnico: tec,
                acompanhante: acomp,
                registrador_chegada: registrador
            })
        });

        const data = await resp.json();

        if(resp.ok && data.sucesso) {
            Swal.fire('Sucesso!', 'Chegada registrada. OS em Andamento!', 'success');
            const mEl = document.getElementById('modalRegistrarChegadaOS');
            if (mEl) {
                const m = bootstrap.Modal.getInstance(mEl);
                if(m) m.hide();
            }
            carregarWidgetDemandasDashboard();
            if(typeof loadOSTable === 'function') loadOSTable();
        } else {
            Swal.fire('Erro', data.mensagem || 'Falha ao registrar.', 'error');
        }
    } catch(err) {
        console.error(err);
        Swal.fire('Erro', 'Erro de rede.', 'error');
    }
});

// ==========================================
// FUNÇÕES GLOBAIS DE CARREGAMENTO
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    fetch('/elevadores/api/elevadoress/tecnicos_otis/')
        .then(res => res.json())
        .then(tecnicos => {
            window.tecnicosOtisCache = tecnicos;
            const outrosSelects = document.querySelectorAll('#edit_os_tecnico, #mpmTecnicoNome, #editMpmTecnicoNome, #concluirMPMTecnico, #pecaTecnicoIdentificador, #concluirTecnico, #editPecaTecnicoIdentificador, #editPecaTecnico, #concluirTecnicoOS, #id_tecnico');
            outrosSelects.forEach(select => {
                let optionsHtml = '<option value="" selected disabled>Selecione o técnico</option>';
                tecnicos.forEach(tec => {
                    optionsHtml += `<option value="${tec}">${tec}</option>`;
                });
                select.innerHTML = optionsHtml;
            });
        })
        .catch(err => console.error('Erro ao buscar técnicos da Otis globais', err));
});

// ==========================================
// FUNÇÕES DE ALARMES EMS
// ==========================================

function carregarAlarmesEms() {
    const tbody = document.getElementById('tabela-alarmes-ems');
    if (!tbody) return;
    
    fetch('/elevadores/api/alarme_ems/')
        .then(res => res.json())
        .then(data => {
            const lista = Array.isArray(data) ? data : (data.results || []);

function carregarAlarmesEms() {
    const tbody = document.getElementById('tabela-alarmes-ems');
    if (!tbody) return;
    
    fetch('/elevadores/api/alarme_ems/')
        .then(res => res.json())
        .then(data => {
            const lista = Array.isArray(data) ? data : (data.results || []);
            
            const tabelaEl = $('#tabela-ems');
            if ($.fn.DataTable.isDataTable(tabelaEl)) {
                tabelaEl.DataTable().destroy();
            }
            
            tbody.innerHTML = '';
            lista.forEach(item => {
                const dateObj = new Date(item.data_hora);
                const dataFmt = dateObj.toLocaleDateString('pt-BR') + ' ' + dateObj.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
                const badgeClass = item.tipo_evento === 'ALARM' ? 'bg-danger' : 'bg-warning text-dark';
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="badge ${badgeClass}">${item.tipo_evento}</span></td>
                    <td>${dataFmt}</td>
                    <td>${item.descricao}</td>
                    <td><span class="badge bg-secondary">${item.elevador}</span></td>
                    <td><span class="text-muted"><i class="bi bi-person me-1"></i>${item.usuario_registrador || '-'}</span></td>
                `;
                tbody.appendChild(tr);
            });
// MISSING LINE 1761
// MISSING LINE 1762
// MISSING LINE 1763
// MISSING LINE 1764
// MISSING LINE 1765
// MISSING LINE 1766
// MISSING LINE 1767
// MISSING LINE 1768
// MISSING LINE 1769
// MISSING LINE 1770
// MISSING LINE 1771
// MISSING LINE 1772
// MISSING LINE 1773
// MISSING LINE 1774
// MISSING LINE 1775
// MISSING LINE 1776
    const tbody = document.getElementById('tabela-alarmes-ems');
    if (!tbody) return;
    
    fetch('/elevadores/api/alarme_ems/')
        .then(res => res.json())
        .then(data => {
            const lista = Array.isArray(data) ? data : (data.results || []);
            
            const tabelaEl = $('#tabela-ems');
            if ($.fn.DataTable.isDataTable(tabelaEl)) {
                tabelaEl.DataTable().destroy();
            }
            
            tbody.innerHTML = '';
            lista.forEach(item => {
                const dateObj = new Date(item.data_hora);
                const dataFmt = dateObj.toLocaleDateString('pt-BR') + ' ' + dateObj.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
                const badgeClass = item.tipo_evento === 'ALARM' ? 'bg-danger' : 'bg-warning text-dark';
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="badge ${badgeClass}">${item.tipo_evento}</span></td>
                    <td>${dataFmt}</td>
                    <td>${item.descricao}</td>
                    <td><span class="badge bg-secondary">${item.elevador}</span></td>
                    <td><span class="text-muted"><i class="bi bi-person me-1"></i>${item.usuario_registrador || '-'}</span></td>
                `;
                tbody.appendChild(tr);
            });
            
            if (typeof DataTable !== 'undefined') {
                new DataTable(tabelaEl[0], {
                    language: { url: 'https://cdn.datatables.net/plug-ins/2.0.3/i18n/pt-BR.json' },
                    order: [[1, 'desc']]
                });
            }
        })
        .catch(err => {
            console.error('Erro ao buscar alarmes EMS', err);
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-danger">Erro ao carregar os dados.</td></tr>';
        });
}

// ==========================================
// FUNﾃ�髭S DE REGISTRO DE PARADAS
// ==========================================

function carregarRegistroParadas() {
    const tbody = document.querySelector('#tabela-paradas-body');
    if (!tbody) return;
    
    fetch('/elevadores/api/registro_paradas/')
        .then(res => res.json())
        .then(data => {
            const lista = Array.isArray(data) ? data : (data.results || []);
            
            const tabelaEl = $('#tabela-paradas');
            if ($.fn.DataTable.isDataTable(tabelaEl)) {
                tabelaEl.DataTable().destroy();
            }
            
            tbody.innerHTML = '';
            lista.forEach(item => {
                const dateIni = new Date(item.data_hora_parada);
                const dataIniFmt = dateIni.toLocaleDateString('pt-BR') + ' ' + dateIni.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
                
                let dataFimFmt = '-';
                if (item.data_hora_retorno) {
                    const dateFim = new Date(item.data_hora_retorno);
                    dataFimFmt = dateFim.toLocaleDateString('pt-BR') + ' ' + dateFim.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'});
                }
                
                let tempoHoras = '-';
                if (item.tempo_parado) {
                    tempoHoras = parseFloat(item.tempo_parado).toFixed(1) + ' h';
                }
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="badge bg-secondary">${item.elevador}</span></td>
                    <td>${dataIniFmt}</td>
                    <td>${dataFimFmt}</td>
                    <td class="fw-bold text-danger">${tempoHoras}</td>
                    <td class="text-center">
                        ${item.os_relacionada ? `<button class="btn btn-sm btn-outline-primary" onclick="mostrarDetalhesElev(${item.os_relacionada})" title="Visualizar O.S relacionada"><i class="bi bi-eye"></i></button>` : '-'}
                    </td>
                `;
                tbody.appendChild(tr);
            });
            
            if (typeof DataTable !== 'undefined') {
                new DataTable(tabelaEl[0], {
                    language: { url: 'https://cdn.datatables.net/plug-ins/2.0.3/i18n/pt-BR.json' },
                    order: [[1, 'desc']]
                });
            }
        })
        .catch(err => {
            console.error('Erro ao buscar registro de paradas', err);
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-danger">Erro ao carregar os dados.</td></tr>';
        });
}

window.salvarAlarmeEms = function() {
    const form = document.getElementById('form-alarme-ems');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const payload = {
        tipo_evento: document.getElementById('alarmeTipo').value,
        data_hora: document.getElementById('alarmeDataHora').value,
        elevador: document.getElementById('alarmeElevador').value,
        descricao: document.getElementById('alarmeDescricao').value
    };

    fetch('/elevadores/api/alarme_ems/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload)
    })
    .then(async res => {
        if (!res.ok) throw new Error('Erro ao salvar alarme');
        return res.json();
    })
    .then(data => {
        const modalEl = document.getElementById('modalRegistrarAlarmeEms');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        form.reset();
        
        // Mostrar Toast de sucesso
        const toastEl = document.getElementById('toastConclusaoSucesso');
        if (toastEl) {
            document.getElementById('toast-msg').innerText = "Alarme EMS registrado com sucesso!";
            const toast = new bootstrap.Toast(toastEl);
            toast.show();
        }
        
        carregarAlarmesEms();
    })
    .catch(err => {
        console.error(err);
        alert('Ocorreu um erro ao registrar o alarme. Tente novamente.');
    });
};

document.addEventListener('DOMContentLoaded', () => {
    // Carregar alarmes quando a aba for clicada
    const emsTab = document.getElementById('ems-tab');
    if (emsTab) {
        emsTab.addEventListener('shown.bs.tab', carregarAlarmesEms);
    }
    
    // Carregar paradas quando a aba for clicada
    const paradasTab = document.getElementById('paradas-tab');
    if (paradasTab) {
        paradasTab.addEventListener('shown.bs.tab', carregarRegistroParadas);
    }
});
// MISSING LINE 1941
// MISSING LINE 1942
// MISSING LINE 1943
// MISSING LINE 1944
// MISSING LINE 1945
// MISSING LINE 1946
// MISSING LINE 1947
// MISSING LINE 1948
// MISSING LINE 1949
// MISSING LINE 1950
// MISSING LINE 1951
// MISSING LINE 1952
// MISSING LINE 1953
// MISSING LINE 1954
// MISSING LINE 1955
// MISSING LINE 1956
// MISSING LINE 1957
// MISSING LINE 1958
// MISSING LINE 1959
// MISSING LINE 1960
// MISSING LINE 1961
// MISSING LINE 1962
// MISSING LINE 1963
// MISSING LINE 1964
// MISSING LINE 1965
// MISSING LINE 1966
// MISSING LINE 1967
// MISSING LINE 1968
// MISSING LINE 1969
    
    const grid = document.getElementById('grid-visao360');
    const loading = document.getElementById('loading-visao360');
    
    grid.style.display = 'none';
    loading.classList.remove('d-none');
    
    fetch(`/elevadores/api/elevadoress/historico_mensal/?mes=${mes}`)
        .then(res => res.json())
        .then(data => {
    const mesAtual = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}`;
    inputMes.value = mesAtual;
    
    inputMes.addEventListener('change', carregarVisao360);
    
    // Carregar ao abrir a aba
    const visao360Tab = document.getElementById('visao360-tab');
    if (visao360Tab) {
        visao360Tab.addEventListener('shown.bs.tab', () => {
            if (Object.keys(dadosVisao360).length === 0) {
                carregarVisao360();
            }
        });
    }
}

function carregarVisao360() {
    const inputMes = document.getElementById('filtroMesVisao360');
    const mes = inputMes.value;
    if (!mes) return;
    
    const grid = document.getElementById('grid-visao360');
    const loading = document.getElementById('loading-visao360');
    
    grid.style.display = 'none';
    loading.classList.remove('d-none');
    
    fetch(`/elevadores/api/elevadoress/historico_mensal/?mes=${mes}`)
        .then(res => res.json())
        .then(data => {
            dadosVisao360 = data;
            renderizarCardsVisao360(mes);
        })
        .catch(err => {
            console.error('Erro ao buscar Visﾃ｣o 360:', err);
            grid.innerHTML = '<div class="alert alert-danger w-100 text-center">Erro ao carregar dados.</div>';
        })
        .finally(() => {
            loading.classList.add('d-none');
            grid.style.display = 'flex';
        });
}

function renderizarCardsVisao360(mesRef) {
    const grid = document.getElementById('grid-visao360');
    grid.innerHTML = '';
    
    // Obter os nomes dos elevadores a partir das chaves do dicionﾃ｡rio
    const elevadores = Object.keys(dadosVisao360);
    
    elevadores.forEach(elev => {
        const eventos = dadosVisao360[elev] || [];
        const qtd = eventos.length;
        
        let cardClass = 'border-success';
        let iconClass = 'bi-check-circle text-success';
        let statusText = 'Intacto (0)';
        let bgStyle = '';
        
        if (qtd > 0) {
            const hasAlarm = eventos.some(e => e.tipo === 'ALARME');
            const hasOS = eventos.some(e => e.tipo === 'OS');
            
            if (hasAlarm || hasOS) {
                cardClass = 'border-danger';
                iconClass = 'bi-exclamation-triangle-fill text-danger';
                bgStyle = 'background-color: #fff5f5;';
            } else {
                cardClass = 'border-warning';
                iconClass = 'bi-info-circle-fill text-warning';
                bgStyle = 'background-color: #fffdf5;';
            }
            statusText = `${qtd} evento(s)`;
        }
        
        const col = document.createElement('div');
        col.className = 'col-12 col-sm-6 col-md-4 col-lg-3';

        const card = document.createElement('div');
        card.className = `card shadow-sm hover-effect-card h-100 ${cardClass}`;
        card.style.cssText = `cursor: pointer; border-width: 2px; border-radius: 10px; ${bgStyle}`;
        card.onclick = () => abrirModalHistoricoElevador(elev, mesRef);
        
        // Mostrar apenas a parte curta do nome (ex: "Social 1" em vez de "Social 1 - M2674")
        const nomeCurto = elev.split(' - ')[0];
        
        card.innerHTML = `
            <div class="card-body text-center p-3 d-flex flex-column justify-content-center">
                <h5 class="fw-bold mb-2">${nomeCurto}</h5>
                <i class="bi ${iconClass} fs-3 mb-2 d-block"></i>
                <small class="text-muted fw-bold">${statusText}</small>
            </div>
        `;
        
        col.appendChild(card);
        grid.appendChild(col);
    });
}

function abrirModalHistoricoElevador(elev, mesRef) {
    const eventos = dadosVisao360[elev] || [];
            const card = document.createElement('div');
            card.className = 'card border shadow-sm rounded-3 mb-2 hover-shadow';
            card.style.cssText = 'transition: all 0.2s ease; cursor: pointer; background: #ffffff;';
            card.onmouseenter = () => { card.style.transform = 'translateY(-2px)'; card.style.boxShadow = '0 .5rem 1rem rgba(0,0,0,.15) !important'; };
            card.onmouseleave = () => { card.style.transform = 'none'; card.style.boxShadow = '0 .125rem .25rem rgba(0,0,0,.075) !important'; };
            
            card.innerHTML = `
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="fw-bold mb-0 text-dark" style="font-size: 0.9rem;">${item.titulo}</h6>
                        <small class="text-muted fw-bold text-uppercase" style="font-size: 0.7rem;"><i class="bi bi-clock me-1"></i>${dataFmt}</small>
                    </div>
                    <p class="text-muted small mb-2" style="line-height: 1.4; font-size: 0.8rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">${item.detalhes}</p>
                    <div class="d-flex justify-content-end align-items-center pt-2 border-top" style="border-color: #f1f3f5 !important;">
                        <div class="text-primary fw-bold" style="font-size: 0.75rem;">Detalhes <i class="bi bi-arrow-right ms-1"></i></div>
                    </div>
                </div>
            `;
            
            card.onclick = () => {
                if (item.tipo === 'OS' && item.id) {
                    bootstrap.Modal.getInstance(document.getElementById('modalHistoricoElevador')).hide();
                    if (typeof mostrarDetalhesElev === 'function') {
                        mostrarDetalhesElev(item.id);
                    }
                } else {
                    document.getElementById('vis-evento-titulo').innerText = `Detalhes: ${item.titulo}`;
                    document.getElementById('vis-evento-elevador').innerText = elev;
                    document.getElementById('vis-evento-datahora').innerText = dataFmt;
                    document.getElementById('vis-evento-detalhes').innerHTML = item.detalhes.replace(/\\n/g, '<br/>');
                    document.getElementById('vis-evento-registrado-por').innerText = item.registrado_por || 'Sistema';
                    
                    const iconContainer = document.getElementById('vis-evento-icon-container');
                    const icon = document.getElementById('vis-evento-icon');
                    
                    iconContainer.className = 'rounded-circle d-flex align-items-center justify-content-center flex-shrink-0';
                    iconContainer.style.width = '48px';
                    iconContainer.style.height = '48px';
                    
                    if (item.tipo === 'ALARME') {
                        iconContainer.classList.add('bg-danger', 'bg-opacity-10', 'text-danger');
                        icon.className = 'bi bi-bell-fill fs-4';
                    } else if (item.tipo === 'MPM') {
                        iconContainer.classList.add('bg-success', 'bg-opacity-10', 'text-success');
                        icon.className = 'bi bi-tools fs-4';
                    } else if (item.tipo === 'PEÇA') {
                        iconContainer.classList.add('bg-info', 'bg-opacity-10', 'text-dark');
                        icon.className = 'bi bi-nut-fill fs-4';
                    } else {
                        iconContainer.classList.add('bg-primary', 'bg-opacity-10', 'text-primary');
