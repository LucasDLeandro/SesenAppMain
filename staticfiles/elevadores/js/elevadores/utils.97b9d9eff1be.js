import {dados_api, loadDataDashboard} from './elev_dashboard.js'

export const listaElevadores = [
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

export function formatDataIso(data) {
    const yyyy = data.getFullYear();
    const mm = String(data.getMonth() + 1).padStart(2, '0');
    const dd = String(data.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
}


export function mesAnoAtual() {
    const agora = new Date();
    const anoAtual = agora.getFullYear();
    const mes = agora.getMonth();

    const dataDiaInicio = new Date(anoAtual, mes, 1).toISOString().substring(0,10)
    const dataDiaFim = new Date(anoAtual, mes + 1, 0).toISOString().substring(0,10)

    const anoAtualInicio = new Date(anoAtual, 0, 1).toISOString().substring(0,10)
    const anoAtualFim = new Date(anoAtual, 11, 31).toISOString().substring(0,10)

    const anoMinimo = 2020
    const qntAnos = (anoAtual - anoMinimo) + 1

    const rangeAnos = Array.from({length: qntAnos}, (_, index) => anoMinimo + index)
    const rangeMesesObject = {
        '01': 'Janeiro',
        '02': 'Fevereiro',
        '03': 'Março',
        '04': 'Abril',
        '05': 'Maio',
        '06': 'Junho',
        '07': 'Julho',
        '08': 'Agosto',
        '09': 'Setembro',
        '10': 'Outubro',
        '11': 'Novembro',
        '12': 'Dezembro'
    }
    

    return {
        inicioAnoAtual: anoAtualInicio,
        fimAnoAtual: anoAtualFim,
        inicioMesAtual: dataDiaInicio,
        fimMesAtual: dataDiaFim,
        ano_atual: anoAtual,
        mes_atual: mes,
        rangeDeAnos: rangeAnos,
        rangeDeMeses: rangeMesesObject
    }
}

export function filtroAnosMeses(filtro, anos, meses) {
       filtro.innerHTML = ''
       if (anos.length === 0) {
           filtro.innerHTML = '<li><span class="dropdown-item text-muted">Nenhum item encontrado</span></li>'
           return;
        }
        
        anos.forEach(ano => {
            let mesesHTML = ''
            
            Object.entries(meses).sort((a, b) => Number(a[0]) - Number(b[0])).forEach(([numMes, nomeMes]) => {
                
                const uniqueIdMes = `chek_mes_${ano}_${numMes}`
                mesesHTML += `
                <div class="form-check ms-3 mb-1">
                <input class="form-check-input filtro-mes" type="checkbox" value="${ano}-${numMes}" data-ano="${ano}" id="${uniqueIdMes}">
                <label class="form-check-label" style="font-size: 0.9em; cursor: pointer;" for="${uniqueIdMes}">${nomeMes}</label>
                </div>
                `
            })
            const uniqueIdAno = `check_${ano}`
            const collapseId = `collapse_meses_${ano}`;
            const opcao = `
            <li class="px-3 py-1" style="list-style-type: none;">
                <div class="d-flex align-items-center">
                    <button class="btn btn-sm btn-link text-decoration-none text-secondary p-0 me-2 fw-bold" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false">
                        +
                    </button>
    
                    <div class="form-check mb-0">
                        <input class="form-check-input filtro-ano" type="checkbox" value="${ano}" id="${uniqueIdAno}">
                        <label class="form-check-label fw-bold" style="cursor: pointer;" for="${uniqueIdAno}">${ano}</label>
                    </div>
                </div>
                
                <div class="collapse mt-2 ms-2" id="${collapseId}">
                    ${mesesHTML}
                </div>
            </li>
            `
            filtro.insertAdjacentHTML('beforeend', opcao)
        })
    }

export async function changeFiltro(event, indicador, parametroX, parametroY, filtroDinamico, corpoChart, layoutChart) {

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

            const dadosFiltrados = await loadDataDashboard({inicio: data_inicio, fim: data_fim})
            let novaCatX = null
            let novaDadosY = null
            if (indicador == 'ind_quatro') {
                novaCatX = [...listaElevadores]
                novaDadosY = listaElevadores.map(nomeElevador => {
                    const elevadorNoBanco = dados_api.ind_quatro.find(item => item.elevador === nomeElevador)

                    return elevadorNoBanco ? elevadorNoBanco.disponibilidade : 100
                })

            } else {
                novaCatX = dadosFiltrados[indicador].map(item => item[parametroX])
                novaDadosY = dadosFiltrados[indicador].map(item => item[parametroY])
            }

            

            const novoTraceChart = [{
                x: novaCatX,
                y: novaDadosY,
                type: 'bar',
                text: novaDadosY
            }]
                
            

            Plotly.react(corpoChart, novoTraceChart, layoutChart)

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

}