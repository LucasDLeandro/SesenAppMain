import {formatDataIso, mesAnoAtual, filtroAnosMeses} from './utils.js';

const data_inicio = document.getElementById('dash-data-inicio') 
const data_fim = document.getElementById('dash-data-fim')
const elev_selecionado = document.getElementById('dash-elevador')

const {inicioMesAtual, fimMesAtual, rangeDeAnos, rangeDeMeses} = mesAnoAtual()

const dadosDashboard = {}

const urlBase = "/ordens/api/elev/dadosDashboard/"

async function loadDataDashboard() {
    
}

let chartIndicadorUm = null
async function dadosIndicadorUm() {

    
    const params = new URLSearchParams();
    if (inicioMesAtual) {
        params.append('inicio', inicioMesAtual)
    }
    if (data_fim) {
        params.append('fim', fimMesAtual)
    }
    if (elev_selecionado) {
        params.append('elev', elev_selecionado.value)
    } 
    

    let urlFiltrada = urlBase

    const strParams = params.toString();
    if (strParams != "") {
        urlFiltrada = urlBase + '?' + strParams  
    }

    console.log(urlFiltrada)

    
    try {
        
        const resposta = await fetch(urlFiltrada)
        const dados_api = await resposta.json()


        const categoriasX = dados_api.ind_um.map(item => item.protocolo)
        const dadosY = dados_api.ind_um.map(item => item.min_chegada)
        const data_hora = dados_api.ind_um.map(item => item.data_hora)

        console.log(data_hora)

        const corpoChart = document.getElementById('chart-1')

        const dadosPlotly = [{
            x: categoriasX,
            y: dadosY,
            type: 'bar',
            text: dadosY
        }]

        const layout = {
            xaxis: {
                type: 'category',
                range: [inicioMesAtual, fimMesAtual]
            },
            height: 500
        }
            
        

        Plotly.newPlot(corpoChart, dadosPlotly, layout)




    } catch (erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }
}

async function dadosIndicadorTres() {
    
    const filtroDinamico = document.getElementById('filtro-dinamico-chart-3')
    const corpoChart = document.getElementById('chart-3')
    

    const params = new URLSearchParams();
    if (inicioMesAtual) {
        params.append('inicio', inicioMesAtual)
    }
    if (data_fim) {
        params.append('fim', fimMesAtual)
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
        const dados_api = await resposta.json()
        
        filtroAnosMeses(filtroDinamico, rangeDeAnos, rangeDeMeses)

        
        const listaElevadores = [
            "Social 1 - M2674", 
            "Social 2 - M2675", 
            "Social 3 - M2676",
            "Social 4 - M2677", 
            "Social 5 - M2678", 
            "Serviço 6 - M2679",
            "Privativo 7 - M2680", 
            "Social 8 - M2681", 
            "Social 9 - M2682",
            "Privativo 10 - M2683", 
            "Social 11 - M2684", 
            "Social 12 - M2685",
            "Social 13 - M2686", 
            "Serviço 14 - M2687"
        ];

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
        
        Plotly.react(corpoChart, dadosPlotly, layout)
        
        filtroDinamico.addEventListener('change', function(event) {
            if (event.target.classList.contains('filtro-mes')) {
        
                const isMarcado = event.target.checked
                const anoMesSelecionado = event.target.getAttribute('data-ano')
                const anoDesteMes = filtroDinamico.querySelector(`.filtro-ano[value="${anoMesSelecionado}"]`)
                
        
                const todosCheckboxes = filtroDinamico.querySelectorAll('input[type="checkbox"]')
        
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
        
                    Plotly.relayout(corpoChart, atualizarLayout)
        
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

async function dadosVisaoGeral() {
    const data_inicio = document.getElementById('dash-data-inicio')

    const {ano_atual, inicioAnoAtual, fimAnoAtual} = mesAnoAtual()

    let anoFiltrado = ""
    if (data_inicio.value === "") {
        anoFiltrado = ano_atual
    } else {
        anoFiltrado = data_inicio.value.substring(0,4)
    }

    const urlElevGrafico = "/ordens/api/os/graficoMensal/"
    const params = new URLSearchParams()

    params.append('ano', anoFiltrado)

    let urlFiltrada = urlElevGrafico

    const strParams = params.toString()
    urlFiltrada = urlElevGrafico + '?' + strParams

    try {
        const resposta = await fetch(urlFiltrada)
        const dados_api = await resposta.json()

        const corpoChart = document.getElementById('chart-5')

        const eixoX = dados_api.dados_grafico.mes_exato
        const eixoY = dados_api.dados_grafico.total_mes

        const dadosPlotly = [
            {
                x: eixoX,
                y: eixoY,
                type: 'bar',
                name: 'Total Mensal: ',
                text: eixoY
            }
        ]

        const layout = {
            xaxis: {
                type: 'date',
                tickformat: '%m/%Y',
                dtick: 'M1',
                range: [inicioAnoAtual, fimAnoAtual],
            },
            yaxis: {
                title: 'total',
                //tickmode: 'linear',
                //automargin: true,
                //autorange: false,
                rangemode: 'tozero'
            },
            height: 500,

        }

        Plotly.react(corpoChart, dadosPlotly, layout)

        
    } catch(erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }

}


const elev_tab_dash = document.getElementById('elev-tab-dash')
elev_tab_dash.addEventListener('click', () => {
    //dadosVisaoGeral();
    dadosIndicadorUm();
    dadosIndicadorTres();
})

const btn_dash_filtro = document.getElementById('dash-btn-filtrar')
btn_dash_filtro.addEventListener('click', () => {
    dadosIndicadorUm();
    dadosIndicadorTres();
})