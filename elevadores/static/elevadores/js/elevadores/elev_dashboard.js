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
        

        const layoutChartUm = {
            xaxis: {
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
        
        const layoutChartQuatro = {
            xaxis: { tickangle: -45, automargin: true },
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

        const layoutChartDois = {
            xaxis: {
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