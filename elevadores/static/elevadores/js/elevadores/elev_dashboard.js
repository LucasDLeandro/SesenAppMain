import {formatDataIso, mesAnoAtual, filtroAnosMeses, changeFiltro, listaElevadores} from './utils.js';

const elev_selecionado = document.getElementById('dash-elevador')

const {inicioMesAtual, fimMesAtual, rangeDeAnos, rangeDeMeses, inicioAnoAtual, fimAnoAtual} = mesAnoAtual()


const urlBase = "/elevadores/api/elev/dadosDashboard/"


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
        
        filtroDinamicoChartTres.addEventListener('change', function(event) {
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
        
                    const atualizarLayout = {
                        'xaxis.range': [data_inicio, data_fim]
                    }
        
                    Plotly.relayout(corpoChartTres, atualizarLayout)
        
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
                }   

            }     
        }) 
    } catch (erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }
}

async function dadosIndicadorQuatro() {
    const filtroDinamicoChartQuatro = document.getElementById('filtro-dinamico-chart-4')
    const corpoChartQuatro = document.getElementById('chart-4')

    try {
        const categoriasX = [...listaElevadores]
        const dadosY = listaElevadores.map(nomeElevador => {
            const elevadorNoBanco = dados_api.ind_quatro.find(item => item.elevador === nomeElevador)
            return elevadorNoBanco ? elevadorNoBanco.disponibilidade : 100
        })

        const textosFormatados = dadosY.map(valor => `${valor}%`)

        const customData = listaElevadores.map(nomeElevador => {
            const elevadorNoBanco = dados_api.ind_quatro.find(item => item.elevador === nomeElevador)
           
            if(elevadorNoBanco) {
                 return [
                    `${elevadorNoBanco.elevador}`,
                    `${elevadorNoBanco.tempo_parado}h`,
                    `${elevadorNoBanco.total_mes}h`,
                    `${elevadorNoBanco.dias_uteis}`,
                    `${elevadorNoBanco.horas_disponiveis}h`,
                ]
                
            } else {
                return [
                    nomeElevador,
                    '-',
                    '-',
                    '-',
                    '-'
                ]
            }
        })
        
        filtroAnosMeses(filtroDinamicoChartQuatro, rangeDeAnos, rangeDeMeses)

        const dadosPlotly = [{
            x: categoriasX,
            y: dadosY,
            mode: 'lines',
            name: 'Meta mensal',
            line: { dash: 'dash', color: 'red' },
            customdata: customData,
            type: 'bar',
            text: textosFormatados,
            hovertemplate: 
                'Elevador: <b>%{customdata[0]}</b><br><br>' +
                'Tempo Parado: <b>%{customdata[1]}</b><br>' +
                'Hrs úteis no Mês Total: <b>%{customdata[2]}</b><br>' +
                'Dias úteis no Mês Total: <b>%{customdata[3]}</b><br>' +
                'Horas Disponíveis: <b>%{customdata[4]}</b><br>' +
                'Disponibilidade: <b>%{y}%</b>' +
                '<extra></extra>',
            textposition: 'auto',

            textfont: {
                size: 16,
                weight: 'bold'
            }
        }]

        const layoutChartQuatro = {
            xaxis: {
                type: 'category',
                categoryorder: 'array',
                categoryarray: [...listaElevadores],
                tickmode: 'linear',

            },
            yaxis: {
                range: [80, 105]
            },
            height: 500,
            hoverlabel: {
                align: 'left'
            },
            shapes: [
                {
                    type: 'line',
                    xref: 'paper',
                    x0: 0,
                    y0: 90,
                    x1: 1,
                    y1: 90,
                    line: {
                        color: 'rgb(255, 0, 0)',
                        width: 2,
                        dash: 'dash' // Opções: 'solid', 'dot', 'dash', 'longdash', 'dashdot'
                    }

                }
            ],
            annotations: [{
            xref: 'paper', 
            x: 1, // Posiciona o texto à direita (95% da largura)
            yref: 'y', 
            y: 90,       // Mesma altura da linha
            text: 'DMM≥90%',
            showarrow: false,
            xanchor: 'left',
            yanchor: 'middle',
            yshift: 10,             // Sobe o texto 10px para não ficar em cima da linha
            font: { color: 'black', size: 12, weight: 'bold' }
        }]
        }

        Plotly.react(corpoChartQuatro, dadosPlotly, layoutChartQuatro)

        filtroDinamicoChartQuatro.addEventListener('change', async function (event) {
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

                    const novaCatX = [...listaElevadores]
                    const novaDadosY = listaElevadores.map(nomeElevador => {
                        const elevadorNoBanco = dadosFiltrados.ind_quatro.find(item => item.elevador === nomeElevador)
                        return elevadorNoBanco ? elevadorNoBanco.disponibilidade : 100
                    })

                    const textFormat = novaDadosY.map(valor => `${valor}%`)

                    const dataCustom = listaElevadores.map(nomeElevador => {
                        const elevadorNoBanco = dadosFiltrados.ind_quatro.find(item => item.elevador === nomeElevador)
                        if (elevadorNoBanco) {
                            return [
                                `${elevadorNoBanco.elevador}`,
                                `${elevadorNoBanco.tempo_parado}h`,
                                `${elevadorNoBanco.total_mes}h`,
                                `${elevadorNoBanco.dias_uteis}`,
                                `${elevadorNoBanco.horas_disponiveis}h`,
                            ]
                        } else {
                            return [
                                nomeElevador,
                                '-',
                                '-',
                                '-',
                                '-'
                            ]
                        }
                    })
        
                    const novoTraceChartQuatro = [{
                        x: novaCatX,
                        y: novaDadosY,
                        customdata: dataCustom,
                        type: 'bar',
                        text: textFormat,
                        hovertemplate: 
                            'Elevador: <b>%{customdata[0]}</b><br><br>' +
                            'Tempo Parado: <b>%{customdata[1]}</b><br>' +
                            'Hrs úteis no Mês Total: <b>%{customdata[2]}</b><br>' +
                            'Dias úteis no Mês Total: <b>%{customdata[3]}</b><br>' +
                            'Horas Disponíveis: <b>%{customdata[4]}</b><br>' +
                            'Disponibilidade: <b>%{y}%</b>' +
                            '<extra></extra>',
                        textposition: 'auto',
                        textfont: {
                            size: 16,
                            weight: 'bold'
                        }
                    }]

                    Plotly.react(corpoChartQuatro, novoTraceChartQuatro, layoutChartQuatro)
        
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
                }   

            }
        })

    } catch (erro) {
        console.error("Erro ao tentar filtrar os dados do Indicador 4", erro);
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

        
    } catch(erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }

}


const elev_tab_dash = document.getElementById('elev-tab-dash')
elev_tab_dash.addEventListener('click', async () => {
    await loadDataDashboard({inicio: inicioMesAtual, fim: fimMesAtual})
    dadosVisaoGeral();
    dadosIndicadorUm();
    dadosIndicadorTres();
    dadosIndicadorQuatro();
})

// const btn_dash_filtro = document.getElementById('dash-btn-filtrar')
// btn_dash_filtro.addEventListener('click', () => {
//     dadosIndicadorUm();
//     dadosIndicadorTres();
// })