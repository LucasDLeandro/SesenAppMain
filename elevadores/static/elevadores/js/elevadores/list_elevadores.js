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

        if (headerText.toLowerCase() === 'ações' || headerText.toLowerCase() === 'ação' || headerText.toLowerCase() === 'acões' || headerText === '') {
            tr.appendChild(th);
            return;
        }

        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control form-control-sm';
        input.placeholder = 'Filtrar ' + headerText;
        input.style.cssText = 'width:100%;font-size:12px;padding:4px 8px;border:1px solid #ced4da;border-radius:4px;background-color:var(--background-body)';

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

window.visualizarOSLista = function(id) {
    if (!window.dadosOrdensElevador) return;
    const os = window.dadosOrdensElevador.find(o => o.id === id);
    if (!os) return;
    
    if (typeof abrirModalVisualizarElev === 'function') {
        abrirModalVisualizarElev(
            os.protocolo || '', 
            os.data_hora || '', 
            os.elevador || '', 
            os.ocorrencia || '', 
            os.aprisionamento ? 'Sim' : 'Não', 
            os.solicitante || '', 
            os.atendente || '', 
            os.status || '', 
            os.elevador_parado || (os.tempo_parado ? os.tempo_parado + 'h' : ''), 
            os.data_hora_chegada || '', 
            os.data_hora_saida || '', 
            os.tmp_chegada || '', 
            os.tmp_saida || '', 
            os.tecnico || '', 
            os.componente || '', 
            os.sub_componente || '', 
            os.servico || '', 
            os.midia || ''
        );
    } else {
        console.error("Função abrirModalVisualizarElev não encontrada.");
    }
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

        window.dadosOrdensElevador = dados_api.tabela_concluidas;

        dados_api.tabela_concluidas.forEach(os => {
            const linhaHTML = `
                <tr>
                    <td><code>${os.protocolo}</code></td>
                    <td class="text-nowrap" data-order="${os.protocolo}">${os.data_hora}</td>
                    <td> <span class="bg-light-subtle text-dark-emphasis">${os.elevador}</span></td>
                    <td>${os.tmp_chegada} min</td>
                    <td>${os.tmp_saida || '0'} min</td>
                    <td>
                        <span class="badge bg-success">${os.status}</span>
                    </td>
                    <td class="text-nowrap text-end">
                        <div class="d-flex flex-nowrap justify-content-end gap-1">
                            <button class="btn btn-sm btn-outline-primary" style="white-space: nowrap;" onclick="visualizarOSLista(${os.id})" title="Visualizar O.S">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-warning" onclick="editarOS(${os.id})" title="Editar"><i class="bi bi-pencil"></i></button>
                            <button class="btn btn-sm btn-outline-danger" onclick="excluirOS(${os.id})" title="Excluir"><i class="bi bi-trash"></i></button>
                        </div>
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
            order: [[1, 'desc']],
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
            responsive: true,
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
        dados_api.tabela_concluidas.forEach(os => {
            const linhaHTML = `
                <tr>
                    <td><code>${os.protocolo}</code></td>
                    <td class="text-nowrap" data-order="${os.protocolo}">${os.data_hora}</td>
                    <td> <span class="bg-light-subtle text-dark-emphasis">${os.elevador}</span></td>
                    <td>${os.tmp_chegada} min</td>
                    <td>${os.tmp_saida || '0'} min</td>
                    <td>
                        <span class="badge bg-success">${os.status}</span>
                    </td>
                    <td class="text-nowrap text-end">
                        <div class="d-flex flex-nowrap justify-content-end gap-1">
                            <button class="btn btn-sm btn-outline-primary" style="white-space: nowrap;" onclick="abrirModalVisualizarElev(&quot;${os.protocolo || ''}&quot;, &quot;${os.data_hora || ''}&quot;, &quot;${os.elevador || ''}&quot;, &quot;${String(os.ocorrencia || '').replace(/\\n/g, ' ').replace(/\"/g, '&amp;quot;')}&quot;, &quot;${os.aprisionamento ? 'Sim' : 'Não'}&quot;, &quot;${os.solicitante || ''}&quot;, &quot;${os.atendente || ''}&quot;, &quot;${os.status || ''}&quot;, &quot;${os.elevador_parado || (os.tempo_parado + 'h')}&quot;, &quot;${os.data_hora_chegada || ''}&quot;, &quot;${os.data_hora_saida || ''}&quot;, &quot;${os.tmp_chegada || ''}&quot;, &quot;${os.tmp_saida || ''}&quot;, &quot;${os.tecnico || ''}&quot;, &quot;${os.componente || ''}&quot;, &quot;${os.sub_componente || ''}&quot;, &quot;${String(os.servico || '').replace(/\\n/g, ' ').replace(/\"/g, '&amp;quot;')}&quot;, &quot;${os.midia || ''}&quot;)" title="Visualizar O.S">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-warning" onclick="editarOS(${os.id})" title="Editar"><i class="bi bi-pencil"></i></button>
                            <button class="btn btn-sm btn-outline-danger" onclick="excluirOS(${os.id})" title="Excluir"><i class="bi bi-trash"></i></button>
                        </div>
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
            order: [[1, 'desc']],
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
            responsive: true,
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


window.editarOS = async function(id) {
    if (!window.userCanEditElevadores) {
        if (typeof Swal !== 'undefined') Swal.fire('Acesso Negado', 'Você não tem permissão para editar ordens de serviço. Apenas supervisores podem realizar esta ação.', 'error');
        else alert('Acesso Negado: Apenas supervisores podem editar.');
        return;
    }

    try {
        const response = await fetch(`/elevadores/api/elevadoress/${id}/`);
        if (!response.ok) throw new Error('Erro ao buscar dados da OS');
        const os = await response.json();

        // Popula os campos
        document.getElementById('edit_os_id').value = os.id || id;
        document.getElementById('edit_os_protocolo').value = os.protocolo || '';
        document.getElementById('edit_os_solicitante').value = os.solicitante || '';
        document.getElementById('edit_os_atendente').value = os.atendente || '';
        document.getElementById('edit_os_elevador').value = os.elevador || '';
        document.getElementById('edit_os_elevador_parado').value = os.elevador_parado || 'ATIVO';
        document.getElementById('edit_os_aprisionamento').checked = os.aprisionamento ? true : false;
        document.getElementById('edit_os_ocorrencia').value = os.ocorrencia || '';
        document.getElementById('edit_os_status').value = os.status || 'ABERTA';
        document.getElementById('edit_os_tecnico').value = os.tecnico || '';

        // Formata data_hora para datetime-local
        if (os.data_hora) {
            // Se for string "dd/mm/yyyy hh:mm" ou ISO. Tentar converter para yyyy-MM-ddThh:mm
            let dateVal = "";
            if (os.data_hora.includes("/")) {
                // assume dd/mm/yyyy hh:mm
                const parts = os.data_hora.split(" ");
                if (parts.length === 2) {
                    const dparts = parts[0].split("/");
                    if (dparts.length === 3) dateVal = `${dparts[2]}-${dparts[1]}-${dparts[0]}T${parts[1]}`;
                }
            } else {
                // assume ISO
                dateVal = os.data_hora.slice(0, 16);
            }
            if (dateVal) document.getElementById('edit_os_data_hora').value = dateVal;
        } else {
            document.getElementById('edit_os_data_hora').value = "";
        }

        const modal = new bootstrap.Modal(document.getElementById('elev-edit-os-modal'));
        modal.show();

    } catch (e) {
        console.error(e);
        if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Não foi possível carregar os dados da OS.', 'error');
    }
}

// Intercepta o form
document.addEventListener("DOMContentLoaded", () => {
    const formEditOs = document.getElementById("elev-edit-os-form");
    if (formEditOs) {
        formEditOs.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (!formEditOs.checkValidity()) {
                formEditOs.reportValidity();
                return;
            }
            const id = document.getElementById("edit_os_id").value;
            
            const formData = new FormData(formEditOs);
            
            // Append explicit fields if needed
            formData.set('data_hora', document.getElementById("edit_os_data_hora").value);
            formData.set('protocolo', document.getElementById("edit_os_protocolo").value);
            formData.set('solicitante', document.getElementById("edit_os_solicitante").value);
            formData.set('atendente', document.getElementById("edit_os_atendente").value);
            formData.set('elevador', document.getElementById("edit_os_elevador").value);
            formData.set('elevador_parado', document.getElementById("edit_os_elevador_parado").value);
            formData.set('aprisionamento', document.getElementById("edit_os_aprisionamento").checked);
            formData.set('ocorrencia', document.getElementById("edit_os_ocorrencia").value);
            formData.set('status', document.getElementById("edit_os_status").value);
            formData.set('tecnico', document.getElementById("edit_os_tecnico").value);

            // Clean empty strings so DRF doesn't complain about "blank=False" if it's not strictly required in PATCH,
            // or if we want to let the form logic handle it.
            for (let [key, val] of Array.from(formData.entries())) {
                if (val === "" || val === null || val === "null") {
                    formData.delete(key);
                }
            }

            try {
                const res = await fetch(`/elevadores/api/elevadoress/${id}/`, {
                    method: "PATCH",
                    headers: { 
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]')?.value || "" 
                    },
                    body: formData
                });

                if (res.ok) {
                    bootstrap.Modal.getInstance(document.getElementById("elev-edit-os-modal")).hide();
                    document.getElementById('ordens-concluidas-tab').click(); // Recarrega tabela
                    if (typeof Swal !== 'undefined') Swal.fire('Sucesso!', 'OS atualizada com sucesso.', 'success');
                } else {
                    const err = await res.json();
                    console.error(err);
                    if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Não foi possível salvar a edição.', 'error');
                }
            } catch (err) {
                console.error(err);
            }
        });
    }
});

window.excluirOS = async function(id) {
    if (!window.userCanEditElevadores) {
        if (typeof Swal !== 'undefined') Swal.fire('Acesso Negado', 'Você não tem permissão para excluir ordens de serviço. Apenas supervisores podem realizar esta ação.', 'error');
        else alert('Acesso Negado: Apenas supervisores podem excluir.');
        return;
    }

    if (typeof Swal !== 'undefined') {
        const result = await Swal.fire({
            title: 'Tem certeza?',
            text: "Deseja realmente apagar esta OS? Esta ação não pode ser desfeita.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sim, excluir!',
            cancelButtonText: 'Cancelar'
        });
        if (!result.isConfirmed) return;
    } else {
        if(!confirm("Deseja realmente apagar esta OS?")) return;
    }

    try {
        const res = await fetch(`/elevadores/api/elevadoress/${id}/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]')?.value || "" }
        });
        if (res.ok) {
            document.getElementById('ordens-concluidas-tab').click(); // Reload tab
            if (typeof Swal !== 'undefined') Swal.fire('Excluída!', 'A OS foi apagada com sucesso.', 'success');
        } else {
            if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Ocorreu um problema ao excluir a OS.', 'error');
            else alert('Erro ao excluir OS');
        }
    } catch(e) { console.error(e); }
}
