
window.initFiltrosDash = function() {
    const anoSelect = document.getElementById('global-ano');
    if (anoSelect) {
        let isFirstTime = false;
        if (anoSelect.options.length === 0) {
            isFirstTime = true;
            const anoAtual = new Date().getFullYear();
            for (let i = 2020; i <= anoAtual; i++) {
                const option = document.createElement('option');
                option.value = i.toString();
                option.text = i.toString();
                anoSelect.appendChild(option);
            }
        }
        
        if (isFirstTime) {
            let mesPrev = new Date().getMonth(); // 0-indexed
            let anoPrev = new Date().getFullYear();
            if (mesPrev === 0) {
                mesPrev = 12;
                anoPrev = anoPrev - 1;
            }
            
            const mesValue = mesPrev.toString().padStart(2, '0');
            const anoValue = anoPrev.toString();
            
            document.getElementById('global-mes').value = mesValue;
            document.getElementById('global-ano').value = anoValue;
            
            console.log('initFiltrosDash set global-mes to', mesValue, 'and global-ano to', anoValue);
        }
    }
};
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
                tickangle: -45,
                automargin: true,
            },
            height: 500
        }
            
        

        Plotly.react(corpoChartUm, dadosPlotly, layoutChartUm)


    } catch (erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }
}

async function dadosIndicadorTres() {
    
    const filtroDinamicoChartTres = document.getElementById('filtro-dinamico-chart-3')
    const corpoChartTres = document.getElementById('chart-3')
    
    try {

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
                mode: 'markers+text',
                textposition: 'middle center',
                textfont: { color: '#000', weight: 'bold' },
                type: 'scatter',
                cliponaxis: false,
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
        
        
        const globalRange3 = getGlobalDateRange();
        const inicioStr3 = globalRange3.inicio || inicioMesAtual;
        const fimStr3 = globalRange3.fim || fimMesAtual;
        
        let dataInicioObj3 = new Date(inicioStr3 + 'T12:00:00');
        dataInicioObj3.setHours(dataInicioObj3.getHours() - 24);
        
        let dataFimObj3 = new Date(fimStr3 + 'T12:00:00');
        dataFimObj3.setHours(dataFimObj3.getHours() + 24);
        
        const rangeInicio3 = dataInicioObj3.toISOString().substring(0, 19).replace('T', ' ');
        const rangeFim3 = dataFimObj3.toISOString().substring(0, 19).replace('T', ' ');

        const layout = {
            
            xaxis: { 
                type: 'date',
                tickformat: '%d/%m',
                dtick: 86400000,
                showgrid: true,
                gridcolor:'#f0f0f0',
                range: [rangeInicio3, rangeFim3],
                tickangle: -45,
                automargin: true,
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
            margin: { l: 150, r: 20, t: 50, b: 50 }, // Margens mais limpas
            hovermode: 'closest' // O tooltip foca na bolha exata que o mouse encostar
        }
        
        Plotly.react(corpoChartTres, dadosPlotly, layout)
        

    } catch (erro) {
        console.error("Erro ao tentar filtrar os dados:", erro);
    }
}


async function dadosVisaoGeral() {
    const corpoChart = document.getElementById('chart-5')
    try {
        const eixoX = dados_api.totalizacao[4]['mes_exato']
        const eixoY = dados_api.totalizacao[4]['total_mes']

                const globalRange = getGlobalDateRange();
        const baseDataStr = globalRange.inicio || inicioMesAtual;
        const anoAtualStr = baseDataStr.substring(0, 4);

        const dataInicio = new Date(`${anoAtualStr}-01-01`);
        dataInicio.setDate(dataInicio.getDate() - 15);
        const inicioAjustado = dataInicio.toISOString().split('T')[0];

        const dataFim = new Date(`${anoAtualStr}-12-31`);
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
        await loadDataDashboard(getGlobalDateRange())
        dadosVisaoGeral();
        dadosIndicadorUm();
        dadosIndicadorDois();
        dadosIndicadorTres();
        dadosIndicadorQuatro();
        atualizarCardsIndicadores();
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    if (window.initFiltrosDash) window.initFiltrosDash();
    const tabDashContent = document.getElementById('tab3-content');
    if (tabDashContent && tabDashContent.classList.contains('active')) {
        await loadDataDashboard(getGlobalDateRange());
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
        let ultimoDiaExec = 0;
        dados_api.ind_dois.forEach(item => {
            if (item.status === 'EXECUTADO' && item.data_execucao) {
                const parts = item.data_execucao.split('/'); // DD/MM/YYYY
                if (parts.length === 3) {
                    const dia = parseInt(parts[0], 10);
                    if (dia > ultimoDiaExec) {
                        ultimoDiaExec = dia;
                    }
                }
            }
        });
        widgetInd2Val.innerText = ultimoDiaExec > 0 ? ultimoDiaExec : '--';
    } else if (widgetInd2Val) {
        widgetInd2Val.innerText = '--';
    }

    const widgetInd3Val = document.getElementById('widget-ind3-val');
    const widgetInd3Elev = document.getElementById('widget-ind3-elev');
    if (widgetInd3Val && widgetInd3Elev && dados_api.ind_tres && dados_api.ind_tres.length > 0) {
        let elevadorMaisChamados = '--';
        let maxChamados = 0;
        
        dados_api.ind_tres.forEach(serie => {
            if (serie.y && serie.y.length > 0 && serie.protocolo && serie.protocolo.length > 0) {
                const chamadosTotais = serie.y.reduce((acc, curr) => acc + parseInt(curr, 10), 0);
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
    } else if (widgetInd3Val) {
        widgetInd3Val.innerText = '--';
        if (widgetInd3Elev) widgetInd3Elev.innerText = '--';
    }

    const widgetInd4Val = document.getElementById('widget-ind4-val');
    const widgetInd4Elev = document.getElementById('widget-ind4-elev');
    if (widgetInd4Val && widgetInd4Elev && dados_api.ind_quatro && dados_api.ind_quatro.length > 0) {
        let elevadorMenorDisp = '--';
        let menorDisp = 100;
        let achouAlgum = false;
        
        dados_api.ind_quatro.forEach(item => {
            if (item.disponibilidade > 0 && item.disponibilidade < menorDisp) {
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

        
        const x_days = [];
        const y_elevs = [];
        const text_status = [];
        const colors = [];
        const custom_data = [];
        
        const globalRange = getGlobalDateRange();
        const baseDataStr = globalRange.inicio || inicioMesAtual;
        const anoAtual = parseInt(baseDataStr.substring(0, 4));
        const mesAtual = parseInt(baseDataStr.substring(5, 7));
        const ultimoDiaAtual = new Date(anoAtual, mesAtual, 0).getDate();

        if(dados_api.ind_dois) {
            dados_api.ind_dois.forEach(item => {
                if(item.status === 'PARADO') {
                    x_days.push(ultimoDiaAtual);
                    y_elevs.push(item.elevador);
                    text_status.push(item.status);
                    colors.push('#6c757d');
                    custom_data.push(['-', '-']);
                } else if(item.status === 'PENDENTE') {
                    x_days.push(ultimoDiaAtual);
                    y_elevs.push(item.elevador);
                    text_status.push(item.status);
                    colors.push('#f59e0b');
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

        // Removed duplicate variables

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
                categoryorder: 'array',
                categoryarray: [...listaElevadores].reverse(),
                automargin: true,
                autorange: false,
                range: [-0.5, listaElevadores.length - 0.5]
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

} catch(erro) {
        console.error("Erro ao renderizar gr├ífico 2:", erro);
        corpoChartDois.innerHTML = '<div class="alert alert-danger m-3">Falha ao carregar gr├ífico.</div>';
    }
}


// === NOVAS FUNCIONALIDADES: ALARMES EMS, REGISTRO PARADAS E VISÃO 360 ===

// 1. Alarmes EMS
function carregarAlarmesEms() {
    const tbody = document.getElementById('tabela-alarmes-ems');
    if (!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted"><div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>Carregando alarmes...</td></tr>';
    
    fetch('/elevadores/api/alarme_ems/')
        .then(res => res.json())
        .then(data => {
            const lista = Array.isArray(data) ? data : (data.results || []);
            
            const tabelaEl = $('#tabela-ems');
            if ($.fn.DataTable.isDataTable(tabelaEl)) {
                tabelaEl.DataTable().destroy();
            }
            
            tbody.innerHTML = '';
            if (lista.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">Nenhum alarme registrado.</td></tr>';
                return;
            }
            
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
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-primary" onclick="abrirModalVisualizarAlarmeEms(${item.id})" title="Visualizar Alarme"><i class="bi bi-eye"></i></button>
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
            console.error('Erro ao buscar alarmes EMS', err);
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-danger">Erro ao carregar os dados.</td></tr>';
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
        
        carregarAlarmesEms();
    })
    .catch(err => {
        console.error(err);
        alert('Ocorreu um erro ao registrar o alarme. Tente novamente.');
    });
};

// 2. Registro de Paradas
function carregarRegistroParadas() {
    const tbody = document.getElementById('tabela-paradas-body');
    if (!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted"><div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>Carregando paradas...</td></tr>';
    
    fetch('/elevadores/api/registro_paradas/')
        .then(res => res.json())
        .then(data => {
            const lista = Array.isArray(data) ? data : (data.results || []);
            
            const tabelaEl = $('#tabela-paradas');
            if ($.fn.DataTable.isDataTable(tabelaEl)) {
                tabelaEl.DataTable().destroy();
            }
            
            tbody.innerHTML = '';
            if (lista.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">Nenhuma parada registrada.</td></tr>';
                return;
            }
            
            lista.forEach(item => {
                const tr = document.createElement('tr');
                let retornoBadge = '-';
                if (item.data_hora_retorno) {
                    const dataRetornoFmt = new Date(item.data_hora_retorno).toLocaleString('pt-BR', {hour: '2-digit', minute:'2-digit', day: '2-digit', month: '2-digit', year: 'numeric'});
                    retornoBadge = `<span class="badge bg-success">${dataRetornoFmt}</span>`;
                } else {
                    retornoBadge = `<span class="badge bg-danger">PARADO</span>`;
                }
                
                const dataInicioFmt = new Date(item.data_hora_parada).toLocaleString('pt-BR', {hour: '2-digit', minute:'2-digit', day: '2-digit', month: '2-digit', year: 'numeric'});
                
                let tempoTotal = '-';
                let impactoBadge = '-';
                
                if (item.data_hora_retorno && item.data_hora_parada) {
                    const diffMs = new Date(item.data_hora_retorno) - new Date(item.data_hora_parada);
                    const diffHrs = diffMs / (1000 * 60 * 60);
                    tempoTotal = diffHrs.toFixed(2);
                    
                    const impacto = ((diffHrs / 720) * 100).toFixed(2);
                    let badgeColor = 'bg-success';
                    if (impacto > 5) badgeColor = 'bg-danger';
                    else if (impacto > 1) badgeColor = 'bg-warning text-dark';
                    impactoBadge = `<span class="badge ${badgeColor}">-${impacto}%</span>`;
                } else if (!item.data_hora_retorno && item.data_hora_parada) {
                    const diffMs = new Date() - new Date(item.data_hora_parada);
                    const diffHrs = diffMs / (1000 * 60 * 60);
                    tempoTotal = diffHrs.toFixed(2) + ' (atual)';
                    const impacto = ((diffHrs / 720) * 100).toFixed(2);
                    impactoBadge = `<span class="badge bg-danger">-${impacto}%</span>`;
                }
                
                tr.innerHTML = `
                    <td><span class="badge bg-secondary">${item.elevador}</span></td>
                    <td>${dataInicioFmt}</td>
                    <td>${retornoBadge}</td>
                    <td class="fw-bold">${tempoTotal}</td>
                    <td>${impactoBadge}</td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-primary" onclick="abrirModalVisualizarParada(${item.id})" title="Visualizar Registro de Parada"><i class="bi bi-eye"></i></button>
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
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-danger">Erro ao carregar os dados.</td></tr>';
        });
}

window.abrirModalVisualizarParada = function(id) {
    fetch(`/elevadores/api/registro_paradas/${id}/`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('visParadaElevador').innerText = data.elevador || '-';
            document.getElementById('visParadaInicio').innerText = data.data_hora_parada ? new Date(data.data_hora_parada).toLocaleString('pt-BR') : '-';
            document.getElementById('visParadaFim').innerText = data.data_hora_retorno ? new Date(data.data_hora_retorno).toLocaleString('pt-BR') : 'Parado';
            document.getElementById('visParadaOS').innerText = data.os_relacionada || 'Nenhuma';
            
            const m = new bootstrap.Modal(document.getElementById('modalVisualizarParada'));
            m.show();
        })
        .catch(err => {
            console.error(err);
            alert('Erro ao carregar os detalhes da parada.');
        });
};

window.abrirModalVisualizarAlarmeEms = function(id) {
    fetch(`/elevadores/api/alarme_ems/${id}/`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('visAlarmeElevador').innerText = data.elevador || '-';
            document.getElementById('visAlarmeTipo').innerText = data.tipo_evento || '-';
            document.getElementById('visAlarmeData').innerText = data.data_hora ? new Date(data.data_hora).toLocaleString('pt-BR') : '-';
            document.getElementById('visAlarmeDescricao').innerText = data.descricao || '-';
            document.getElementById('visAlarmeUsuario').innerText = data.usuario_registrador || '-';
            
            const m = new bootstrap.Modal(document.getElementById('modalVisualizarAlarmeEms'));
            m.show();
        })
        .catch(err => {
            console.error(err);
            alert('Erro ao carregar os detalhes do alarme.');
        });
};

// 3. Visão 360
function carregarVisao360() {
    const inputMes = document.getElementById('filtroMesVisao360');
    if (!inputMes) return;
    
    // Set current month if empty
    if (!inputMes.value) {
        const hoje = new Date();
        inputMes.value = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}`;
    }
    
    renderizarCardsVisao360(inputMes.value);
    
    inputMes.addEventListener('change', (e) => {
        renderizarCardsVisao360(e.target.value);
    });
}

function renderizarCardsVisao360(mes) {
    const grid = document.getElementById('grid-visao360');
    const loading = document.getElementById('loading-visao360');
    if (!grid || !loading) return;
    
    grid.style.display = 'none';
    loading.classList.remove('d-none');
    
    fetch(`/elevadores/api/elevadoress/historico_mensal/?mes=${mes}`)
        .then(res => res.json())
        .then(data => {
            loading.classList.add('d-none');
            grid.style.display = 'grid';
            grid.innerHTML = '';
            
            if (!data || data.length === 0) {
                grid.innerHTML = '<div class="col-12 text-center text-muted">Nenhum histórico encontrado.</div>';
                grid.style.display = 'block';
                return;
            }
            
            data.forEach(elev => {
                const card = document.createElement('div');
                card.className = 'card border-0 shadow-sm h-100 rounded-4';
                
                let eventosHTML = '';
                if (elev.eventos && elev.eventos.length > 0) {
                    eventosHTML = '<div class="mt-3">';
                    const eventosMax = elev.eventos.slice(0, 3);
                    eventosMax.forEach(ev => {
                        let icon = 'bi-record-circle';
                        let color = 'text-primary';
                        if (ev.tipo === 'ALARME') { icon = 'bi-bell-fill'; color = 'text-danger'; }
                        else if (ev.tipo === 'MPM') { icon = 'bi-tools'; color = 'text-success'; }
                        else if (ev.tipo === 'PEÇA') { icon = 'bi-nut-fill'; color = 'text-info'; }
                        
                        eventosHTML += `
                            <div class="d-flex align-items-center mb-2 small">
                                <i class="bi ${icon} ${color} me-2"></i>
                                <span class="text-truncate" title="${ev.titulo}">${ev.titulo}</span>
                            </div>
                        `;
                    });
                    
                    if (elev.eventos.length > 3) {
                        eventosHTML += `<div class="text-center mt-2"><span class="badge bg-light text-secondary">+ ${elev.eventos.length - 3} eventos</span></div>`;
                    }
                    eventosHTML += '</div>';
                } else {
                    eventosHTML = '<div class="mt-3 text-center text-muted small"><i class="bi bi-check-circle me-1"></i>Sem ocorrências</div>';
                }
                
                card.innerHTML = `
                    <div class="card-body d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="mb-0 fw-bold text-secondary">${elev.elevador}</h6>
                            <span class="badge bg-primary rounded-pill">${elev.disponibilidade}% Disp</span>
                        </div>
                        <div class="text-muted small mb-2"><i class="bi bi-clock me-1"></i>Parado: ${elev.tempo_parado_str}</div>
                        <hr class="my-2">
                        <div class="flex-grow-1">
                            ${eventosHTML}
                        </div>
                        <div class="mt-3 text-center">
                            <button class="btn btn-sm btn-outline-primary rounded-pill w-100" onclick="abrirModalHistoricoElevador('${elev.elevador}', '${mes}')">
                                Ver Histórico Completo
                            </button>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
        })
        .catch(err => {
            console.error('Erro ao buscar histórico', err);
            loading.classList.add('d-none');
            grid.style.display = 'block';
            grid.innerHTML = '<div class="col-12 text-center text-danger">Erro ao carregar visão 360.</div>';
        });
}

window.abrirModalHistoricoElevador = function(elevador, mes) {
    const modalBody = document.getElementById('modalVisao360Body');
    if (!modalBody) return;
    
    modalBody.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>';
    
    const modal = new bootstrap.Modal(document.getElementById('modalVisao360'));
    modal.show();
    
    fetch(`/elevadores/api/elevadoress/historico_mensal/?mes=${mes}`)
        .then(res => res.json())
        .then(data => {
            const elevData = data.find(d => d.elevador === elevador);
            if (!elevData) {
                modalBody.innerHTML = '<div class="alert alert-warning">Elevador não encontrado.</div>';
                return;
            }
            
            let html = `
                <div class="card bg-light border-0 mb-4 rounded-4">
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-4">
                                <h6 class="text-muted mb-1 small">Disponibilidade</h6>
                                <h4 class="mb-0 fw-bold text-primary">${elevData.disponibilidade}%</h4>
                            </div>
                            <div class="col-4 border-start border-end">
                                <h6 class="text-muted mb-1 small">Eventos</h6>
                                <h4 class="mb-0 fw-bold text-dark">${elevData.eventos.length}</h4>
                            </div>
                            <div class="col-4">
                                <h6 class="text-muted mb-1 small">Tempo Parado</h6>
                                <h5 class="mb-0 fw-bold text-danger">${elevData.tempo_parado_str}</h5>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            if (elevData.eventos.length === 0) {
                html += '<div class="text-center text-muted my-5"><i class="bi bi-check-circle fs-1 d-block mb-3"></i>Nenhum evento registrado neste mês.</div>';
            } else {
                html += '<div class="timeline">';
                elevData.eventos.forEach(ev => {
                    const dataFmt = new Date(ev.data).toLocaleString('pt-BR', {day: '2-digit', month: '2-digit', hour: '2-digit', minute:'2-digit'});
                    
                    let icon = 'bi-record-circle';
                    let bg = 'bg-primary';
                    let text = 'text-primary';
                    
                    if (ev.tipo === 'ALARME') { icon = 'bi-bell-fill'; bg = 'bg-danger'; text = 'text-danger'; }
                    else if (ev.tipo === 'MPM') { icon = 'bi-tools'; bg = 'bg-success'; text = 'text-success'; }
                    else if (ev.tipo === 'PEÇA') { icon = 'bi-nut-fill'; bg = 'bg-info'; text = 'text-info'; }
                    
                    html += `
                        <div class="d-flex mb-4">
                            <div class="${bg} rounded-circle d-flex align-items-center justify-content-center text-white me-3 flex-shrink-0 shadow-sm" style="width: 40px; height: 40px;">
                                <i class="bi ${icon}"></i>
                            </div>
                            <div class="card border-0 shadow-sm flex-grow-1 rounded-4">
                                <div class="card-body p-3">
                                    <div class="d-flex justify-content-between mb-2">
                                        <h6 class="mb-0 fw-bold ${text}">${ev.tipo}</h6>
                                        <span class="text-muted small"><i class="bi bi-clock me-1"></i>${dataFmt}</span>
                                    </div>
                                    <h6 class="mb-1">${ev.titulo}</h6>
                                    <p class="mb-0 text-muted small">${ev.detalhes ? ev.detalhes.substring(0, 100) + (ev.detalhes.length > 100 ? '...' : '') : 'Sem detalhes.'}</p>
                                    ${ev.os_relacionada ? `
                                        <button class="btn btn-sm btn-outline-primary mt-2 rounded-pill px-3" onclick="mostrarDetalhesElev(${ev.os_relacionada})">
                                            <i class="bi bi-eye me-1"></i> Ver O.S
                                        </button>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
            }
            
            modalBody.innerHTML = html;
        })
        .catch(err => {
            console.error(err);
            modalBody.innerHTML = '<div class="alert alert-danger">Erro ao carregar o histórico.</div>';
        });
};

// Event Listeners for Tabs
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
    
    // Carregar visão 360 quando a aba for clicada
    const visao360Tab = document.getElementById('visao360-tab');
    if (visao360Tab) {
        visao360Tab.addEventListener('shown.bs.tab', carregarVisao360);
    }
});


// --- DEMANDAS PENDENTES (APPENDED) ---
window.abrirModalDemandasPendentes = async function() {
    if (window.isFetchingDemandas) return;
    window.isFetchingDemandas = true;
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
                if (!o.min_chegada && (o.status === 'ABERTA' || o.status === 'EM ANDAMENTO' || o.status === 'AGUARDANDO PEÇAS')) {
                    const minPassados = Math.floor((new Date() - new Date(o.data_hora)) / 60000);
                    tempo = `${minPassados} min`;
                }
                demandas.push({
                    tipo: 'os',
                    dataOrigem: o.data_hora,
                    dataExibicao: new Date(o.data_hora).toLocaleDateString('pt-BR'),
                    ref: o.protocolo,
                    tipoNome: o.status === 'ABERTA' ? '<span class="badge bg-secondary">OS Aberta</span>' : (o.status === 'AGUARDANDO PEÇAS' ? '<span class="badge bg-warning text-dark">Pendente</span>' : '<span class="badge bg-primary">Em Andamento</span>'),
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
                    dataOrigem: p.created_at || p.data_registro || new Date().toISOString(),
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
                        btnAction = `<button class="btn btn-sm btn-primary fw-bold shadow-sm" data-bs-dismiss="modal" onclick="setTimeout(() => abrirModalRegistrarChegada('${osStr}'), 400)"><i class="bi bi-person-walking me-1"></i>Iniciar Atendimento</button>`;
                    } else {
                        btnAction = `<button class="btn btn-sm btn-success fw-bold shadow-sm" data-bs-dismiss="modal" onclick="setTimeout(() => abrirModalElevConcluir(${d.id}, '${d.ref}'), 400)"><i class="bi bi-check2-circle me-1"></i>Concluir O.S.</button>`;
                    }
                } else if (d.tipo === 'peca') {
                    const pecaStr = encodeURIComponent(JSON.stringify(d.extra));
                    btnAction = `
                        <div class="d-flex flex-nowrap gap-1">
                            <button class="btn btn-sm btn-outline-primary" style="white-space: nowrap;" data-bs-dismiss="modal" onclick="setTimeout(() => abrirVisualizarPeca('${pecaStr}'), 400)" title="Visualizar Peça">
                                <i class="bi bi-eye"></i>
                            </button>
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
        
    } catch(e) {
        console.error("Erro ao abrir modal", e);
    } finally {
        window.isFetchingDemandas = false;
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

        const outrosSelects = document.querySelectorAll('#edit_os_tecnico, #mpmTecnicoNome, #editMpmTecnicoNome, #concluirMPMTecnico, #pecaTecnicoIdentificador, #concluirTecnico, #editPecaTecnicoIdentificador, #editPecaTecnico, #concluirTecnicoOS, #id_tecnico');
        outrosSelects.forEach(select => {
            let optionsHtml = '<option value="" selected disabled>Selecione o técnico</option>';
            tecnicos.forEach(tec => {
                optionsHtml += `<option value="${tec}">${tec}</option>`;
            });
            select.innerHTML = optionsHtml;
        });
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


// --- WIDGET DEMANDAS PENDENTES (APPENDED) ---
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
                if (!o.min_chegada && (o.status === 'ABERTA' || o.status === 'EM ANDAMENTO' || o.status === 'AGUARDANDO PEÇAS')) {
                    const minPassados = Math.floor((new Date() - new Date(o.data_hora)) / 60000);
                    tempo = `${minPassados} min`;
                }
                demandas.push({
                    tipo: 'os',
                    dataOrigem: o.data_hora,
                    dataExibicao: new Date(o.data_hora).toLocaleDateString('pt-BR'),
                    ref: o.protocolo,
                    tipoNome: o.status === 'ABERTA' ? '<span class="badge bg-secondary">OS Aberta</span>' : (o.status === 'AGUARDANDO PEÇAS' ? '<span class="badge bg-warning text-dark">Pendente</span>' : '<span class="badge bg-primary">Em Andamento</span>'),
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
            
            const cardTitulo = document.getElementById('titulo-widget-recebidas');
            const cardBadge = document.getElementById('badge-demandas-pendentes');
            const cardRodape = document.getElementById('rodape-widget-recebidas');
            const cardWidget = document.getElementById('card-widget-recebidas');

            if (demandas.length === 0) {
                if (cardTitulo) {
                    cardTitulo.classList.remove('text-danger');
                    cardTitulo.classList.add('text-success');
                    cardTitulo.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>Status: Tudo em Dia';
                }
                if (cardBadge) {
                    cardBadge.classList.remove('bg-danger', 'pulse-badge');
                    cardBadge.classList.add('bg-success');
                }
                if (cardRodape) {
                    cardRodape.classList.add('d-none');
                }
                if (cardWidget) {
                    cardWidget.classList.remove('widget-recebidas-alerta');
                    cardWidget.style.border = '1px solid #dee2e6';
                }
                listGroup.innerHTML = '<div class="text-center text-secondary py-3"><i class="bi bi-emoji-smile text-secondary me-2"></i>Nenhuma solicitação pendente! Tudo em dia.</div>';
            } else {
                if (cardTitulo) {
                    cardTitulo.classList.remove('text-success');
                    cardTitulo.classList.add('text-danger');
                    cardTitulo.innerHTML = '<i class="bi bi-exclamation-octagon-fill me-2 pulse-icon"></i>Atenção: Demandas Pendentes';
                }
                if (cardBadge) {
                    cardBadge.classList.remove('bg-success');
                    cardBadge.classList.add('bg-danger', 'pulse-badge');
                }
                if (cardRodape) {
                    cardRodape.classList.remove('d-none');
                }
                if (cardWidget) {
                    cardWidget.classList.add('widget-recebidas-alerta');
                    cardWidget.style.border = '';
                }
                
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


// Global Filter Logic
function getGlobalDateRange() {
    const mesElement = document.getElementById('global-mes');
    const anoElement = document.getElementById('global-ano');
    
    if (!mesElement || !anoElement) return {};
    
    const mes = mesElement.value;
    const ano = anoElement.value;
    
    if(!mes || !ano) return {};
    
    const inicio = `${ano}-${mes}-01`;
    const ultimoDia = new Date(ano, parseInt(mes), 0).getDate();
    const fim = `${ano}-${mes}-${ultimoDia}`;
    return {inicio, fim};
}

document.addEventListener('DOMContentLoaded', () => {
    window.initFiltrosDash();

    const btnAtualizar = document.getElementById('btn-atualizar-dashboard');
    if (btnAtualizar) {
        btnAtualizar.addEventListener('click', async () => {
            const btn = btnAtualizar;
            const textOrig = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Atualizando...';
            btn.disabled = true;

            const range = getGlobalDateRange();
            await loadDataDashboard(range);
            try {
                dadosVisaoGeral();
                dadosIndicadorUm();
                dadosIndicadorDois();
                dadosIndicadorTres();
                dadosIndicadorQuatro();
                atualizarCardsIndicadores();
            } catch (e) {
                console.error("Erro ao atualizar gráficos:", e);
            }

            btn.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Atualizar Gráficos';
            btn.disabled = false;
        });
    }
});

window.carregarTecnicosGlobais = function() {
    if (window.tecnicosOtisCache) {
        preencherSelectsTecnicos(window.tecnicosOtisCache);
    } else {
        fetch('/elevadores/api/elevadoress/tecnicos_otis/')
            .then(res => res.json())
            .then(tecnicos => {
                window.tecnicosOtisCache = tecnicos;
                preencherSelectsTecnicos(tecnicos);
            })
            .catch(err => console.error('Erro ao buscar tecnicos', err));
    }

    function preencherSelectsTecnicos(tecnicos) {
        const $selectTecnico = $('#chegadaTecnico');
        if ($selectTecnico.length) {
            $selectTecnico.empty();
            $selectTecnico.append(new Option('', '', false, false));
            tecnicos.forEach(tec => {
                $selectTecnico.append(new Option(tec, tec, false, false));
            });
            $selectTecnico.val(null).trigger('change');
        }

        const outrosSelects = document.querySelectorAll('#edit_os_tecnico, #mpmTecnicoNome, #editMpmTecnicoNome, #concluirMPMTecnico, #pecaTecnicoIdentificador, #concluirTecnico, #editPecaTecnicoIdentificador, #editPecaTecnico, #concluirTecnicoOS, #id_tecnico');
        outrosSelects.forEach(select => {
            let optionsHtml = '<option value="" selected disabled>Selecione o tcnico</option>';
            tecnicos.forEach(tec => {
                optionsHtml += `<option value="${tec}">${tec}</option>`;
            });
            select.innerHTML = optionsHtml;
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    if (window.carregarTecnicosGlobais) {
        window.carregarTecnicosGlobais();
    }
});
