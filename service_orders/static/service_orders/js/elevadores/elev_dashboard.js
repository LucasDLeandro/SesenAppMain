import {formatDataIso, mesAnoAtual} from './utils.js';

const data_inicio = document.getElementById('dash-data-inicio') 
const data_fim = document.getElementById('dash-data-fim')
const elev_selecionado = document.getElementById('dash-elevador')

let chartIndicadorUm = null
async function dadosIndicadorUm() {

    if (data_inicio.value === "" && data_fim.value === "") {
        
        const {inicio, fim} = mesAnoAtual()

        const inicioFormatado = formatDataIso(inicio)
        const fimFormatado = formatDataIso(fim)

        data_inicio.value = inicioFormatado
        data_fim.value = fimFormatado
    }

    const urlElevDados = '/ordens/api/os/listaOs/api_indicador_um'

    const params = new URLSearchParams();

    if (data_inicio) {
        params.append('inicio', data_inicio.value)
    }
    if (data_fim) {
        params.append('fim', data_fim.value)
    }
    if (elev_selecionado) {
        params.append('elev', elev_selecionado.value)
    } 
    

    let urlFiltrada = urlElevDados

    const strParams = params.toString();
    if (strParams != "") {
        urlFiltrada = urlElevDados + '?' + strParams  
    }

    
    try {

        const resposta = await fetch(urlFiltrada)
        const dados_api = await resposta.json()

        const categoriasX = dados_api.indicador_um.map(item => item.protocolo)
        const dadosY = dados_api.indicador_um.map(item => item.min_chegada)

        const corpoChart = document.getElementById('chart-1')

        let options = {
            chart: {
                type: 'bar'
            },
            series: [{
                name: 'tma',
                data: dadosY,
            }],
            xaxis: {
                categories: categoriasX
            }
        }
        if (chartIndicadorUm !== null) {
            chartIndicadorUm.destroy()
        }

        chartIndicadorUm = new ApexCharts(corpoChart, options)
        chartIndicadorUm.render()

    } catch (erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }
}

let chartIndicadorTres = null
async function dadosIndicadorTres() {
    if (data_inicio.value === "" && data_fim.value === "") {
        
        const {inicio, fim} = mesAnoAtual()

        const inicioFormatado = formatDataIso(inicio)
        const fimFormatado = formatDataIso(fim)

        data_inicio.value = inicioFormatado
        data_fim.value = fimFormatado
    }

    const urlElevDados = '/ordens/api/os/listaOs/api_indicador_tres'
    const params = new URLSearchParams();

    if (data_inicio) {
        params.append('inicio', data_inicio.value)
    }
    if (data_fim) {
        params.append('fim', data_fim.value)
    }
    if (elev_selecionado) {
        params.append('elev', elev_selecionado.value)
    }

    let urlFiltrada = urlElevDados

    const strParams = params.toString();
    if (strParams != "") {
        urlFiltrada = urlElevDados + '?' + strParams  
    }

    try {

        const resposta = await fetch(urlFiltrada)
        const dados_api = await resposta.json()

        const corpoChart = document.getElementById('chart-3')

        const agrupamento = {}

        const listaElevadores = [
            "Social 1 - M2674", "Social 2 - M2675", "Social 3 - M2676",
            "Social 4 - M2677", "Social 5 - M2678", "Serviço 6 - M2679",
            "Privativo 7 - M2680", "Social 8 - M2681", "Social 9 - M2682",
            "Privativo 10 - M2683", "Social 11 - M2684", "Social 12 - M2685",
            "Social 13 - M2686", "Serviço 14 - M2687"
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

        

        console.log(dadosPlotly)

        const layout = {
            
            xaxis: { 
                type: 'date',
                tickformat: '%d/%m/%Y', // Formatação brasileira
                dtick: 86400000,
                showgrid: true,
                gridcolor:'#f0f0f0',
                range: [data_inicio.value, data_fim.value]
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


       


    } catch (erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }
}


const elev_tab_dash = document.getElementById('elev-tab-dash')
elev_tab_dash.addEventListener('click', () => {
    dadosIndicadorUm();
    dadosIndicadorTres();
})

const btn_dash_filtro = document.getElementById('dash-btn-filtrar')
btn_dash_filtro.addEventListener('click', () => {
    dadosIndicadorUm();
    dadosIndicadorTres();
})