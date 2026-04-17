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
    const {inicio, fim} = mesAnoAtual
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