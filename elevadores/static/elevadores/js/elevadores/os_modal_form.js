// Função utilitária para aplicar filtros de pesquisa individual por coluna
function aplicarFiltroColunasModal(tabela) {
    var tableNode = tabela.table().node();
    var thead = tableNode.querySelector('thead');
    
    if (thead.querySelector('.filter-row')) return;

    var tr = document.createElement('tr');
    tr.className = 'filter-row';

    tabela.columns().every(function(index) {
        var column = this;
        var headerText = column.header().textContent.trim();
        var th = document.createElement('th');

        if (headerText.toLowerCase() === 'ações' || headerText.toLowerCase() === 'acões' || headerText === '') {
            tr.appendChild(th);
            return;
        }

        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-control form-control-sm';
        input.placeholder = 'Filtrar ' + headerText;
        input.style.cssText = 'width:100%;font-size:12px;padding:4px 8px;border:1px solid #ced4da;border-radius:4px;background-color:#f8f9fa';

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

const modal_os_criar = new bootstrap.Modal(document.getElementById('elev-create-os-modal'));
const form_os_criar = document.getElementById('elev-create-os-form');

const modal_os_concluir= new bootstrap.Modal(document.getElementById('elev-concluir-os-modal'));
const form_os_concluir = document.getElementById('elev-concluir-os-form');


//const urlElevCriarOs = form_os_criar.getAttribute('data-url-elev-criar-os');
//const urlElevConcluirOsBase = form_os_concluir.getAttribute('data-url-elev-concluir-os');

const btn_solicitar_elev_os = document.getElementById('elev-btn-solicitar-os')
btn_solicitar_elev_os.addEventListener("click", abrirModalElevSolicitar)

function abrirModalElevSolicitar() {
    form_os_criar.reset();

    id_oculto_elev_os_criar = document.getElementById('id_oculto_elev_os');
    id_oculto_elev_os_criar = "";

    const urlElevRegistrarOsReal = `/elevadores/api/elevadoress/`
    form_os_criar.action = urlElevRegistrarOsReal

    modal_os_criar.show();
}

function abrirModalElevConcluir(id_os, protocolo) {
    document.getElementById('id_oculto_elev_os_concluir').value = id_os
    
    // Set field values
    const inputProtocolo = document.getElementById('id_protocolo');
    if (inputProtocolo) inputProtocolo.value = protocolo;

    const urlElevConcluirOsReal = `/elevadores/api/elevadoress/${id_os}/concluir_elev_os/`
    form_os_concluir.action = urlElevConcluirOsReal

    const modalAbertasNode = document.getElementById('modal-lista-abertas-elev');
    if (modalAbertasNode) {
        const modalAbertas = bootstrap.Modal.getInstance(modalAbertasNode);
        if (modalAbertas) modalAbertas.hide();
    }
    
    // Fetch read-only info
    const loadingInfo = document.getElementById('concluirLoadingInfo');
    const dadosInfo = document.getElementById('concluirDadosInfo');
    
    if (loadingInfo && dadosInfo) {
        loadingInfo.classList.remove('d-none');
        dadosInfo.classList.add('d-none');
        
        fetch(`/elevadores/api/elevadoress/${id_os}/`)
            .then(res => res.json())
            .then(data => {
                document.getElementById('concluirReadonlyProtocolo').value = data.protocolo || '';
                document.getElementById('concluirReadonlyElevador').value = data.elevador || '';
                
                if(data.data_hora) {
                    const dt = new Date(data.data_hora);
                    document.getElementById('concluirReadonlyDataAbertura').value = dt.toLocaleString('pt-BR');
                }
                
                document.getElementById('concluirReadonlyOcorrencia').value = data.ocorrencia || '';
                
                // Pre-fill fields from Registrar Chegada
                if(data.data_hora_chegada) {
                    const dtC = new Date(data.data_hora_chegada);
                    const dtChegada = new Date(dtC.getTime() - (dtC.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
                    const fieldChegada = document.getElementById('id_data_hora_chegada');
                    if (fieldChegada) fieldChegada.value = dtChegada;
                } else {
                    const fieldChegada = document.getElementById('id_data_hora_chegada');
                    if (fieldChegada) fieldChegada.value = '';
                }

                if(data.tecnico) {
                    const fieldTecnico = document.getElementById('concluirTecnicoOS');
                    if (fieldTecnico) fieldTecnico.value = data.tecnico;
                } else {
                    const fieldTecnico = document.getElementById('concluirTecnicoOS');
                    if (fieldTecnico) fieldTecnico.value = '';
                }
                
                // Lógica visual para OS Aguardando Peças
                const selectPecas = document.getElementById('id_houve_substituicao_pecas');
                let alertContainer = document.getElementById('alert-os-pendente');
                if (!alertContainer) {
                    alertContainer = document.createElement('div');
                    alertContainer.id = 'alert-os-pendente';
                    dadosInfo.prepend(alertContainer);
                }

                if (data.status === 'AGUARDANDO PEÇAS') {
                    if (selectPecas) {
                        selectPecas.value = 'Não houve necessidade';
                        selectPecas.closest('.mb-3') ? selectPecas.closest('.mb-3').style.display = 'none' : selectPecas.style.display = 'none';
                    }
                    const selectStatus = document.getElementById('id_status');
                    if (selectStatus) selectStatus.value = 'CONCLUIDA';
                    
                    alertContainer.innerHTML = '<div class="alert alert-info py-2" role="alert"><i class="bi bi-info-circle me-2"></i><strong>Atenção:</strong> A peça que estava pendente será dada como substituída com sucesso, com a data e horário definidos acima.</div>';
                } else {
                    if (selectPecas) {
                        selectPecas.value = 'Não houve necessidade';
                        selectPecas.closest('.mb-3') ? selectPecas.closest('.mb-3').style.display = 'block' : selectPecas.style.display = 'block';
                    }
                    alertContainer.innerHTML = '';
                }

                loadingInfo.classList.add('d-none');
                dadosInfo.classList.remove('d-none');
            })
            .catch(err => {
                console.error("Erro ao buscar detalhes da OS: ", err);
                loadingInfo.innerHTML = '<span class="text-danger">Erro ao carregar dados.</span>';
            });
    }

    modal_os_concluir.show()
}

const hora_chegada = document.getElementById('id_data_hora_chegada')
const hora_conclusao = document.getElementById('id_data_hora_conclusao')

hora_chegada.addEventListener('change', function() {
    hora_conclusao.value = hora_chegada.value
})

const houveSubstituicaoPecas = document.getElementById('id_houve_substituicao_pecas');
const containerPecaSubstituida = document.getElementById('container-peca-substituida');
const pecaSubstituidaInput = document.getElementById('id_peca_substituida');

if (houveSubstituicaoPecas) {
    houveSubstituicaoPecas.addEventListener('change', function() {
        if (this.value === 'Sim_Imediata' || this.value === 'Sim_Posterior' || this.value.startsWith('Sim')) {
            containerPecaSubstituida.style.display = 'block';
            pecaSubstituidaInput.required = true;
        } else {
            containerPecaSubstituida.style.display = 'none';
            pecaSubstituidaInput.required = false;
            pecaSubstituidaInput.value = '';
        }
    });
}

// Lógica para Justificativa de Parada
const selectElevadorParado = document.querySelector('#form-os-concluir select[name="elevador_parado"]');
const containerJustificativaParada = document.getElementById('container-justificativa-parada');
const justificativaParadaInput = document.getElementById('id_justificativa_parada');

if (selectElevadorParado) {
    selectElevadorParado.addEventListener('change', function() {
        if (this.value === 'PARADO') {
            containerJustificativaParada.style.display = 'block';
            if (justificativaParadaInput) justificativaParadaInput.required = true;
        } else {
            containerJustificativaParada.style.display = 'none';
            if (justificativaParadaInput) {
                justificativaParadaInput.required = false;
                justificativaParadaInput.value = '';
            }
        }
    });
    // Dispara no carregamento inicial caso venha preenchido
    selectElevadorParado.dispatchEvent(new Event('change'));
}

// Lógica do Sistema EMS (Múltiplos Elevadores)
const selectElevadorCriar = document.getElementById('id_elevador');
const containerElevadoresEms = document.getElementById('container-elevadores-ems');
const select2Ems = $('#id_elevadores_ems');
const emsHidden = document.getElementById('id_elevadores_ems_hidden');

if (selectElevadorCriar) {
    // Inicia select2 do EMS
    select2Ems.select2({
        theme: 'bootstrap-5',
        dropdownParent: $('#elev-create-os-modal'),
        placeholder: 'Selecione os elevadores...',
        allowClear: true
    });

    selectElevadorCriar.addEventListener('change', function() {
        if (this.value === 'Sistema EMS') {
            containerElevadoresEms.style.display = 'block';
        } else {
            containerElevadoresEms.style.display = 'none';
        }
    });

    $('#btn-ems-select-all').on('click', () => {
        const todosOpts = select2Ems.find('option').map(function() { return this.value }).get();
        select2Ems.val(todosOpts).trigger('change');
    });

    $('#btn-ems-clear-all').on('click', () => {
        select2Ems.val(null).trigger('change');
    });
}

form_os_criar.addEventListener('submit', async function(evento_elev_criar_os) {
    evento_elev_criar_os.preventDefault();

    const urlElevCriarDestino = form_os_criar.action;
    
    // Antes de empacotar o form, salva os valores múltiplos no hidden input
    if (selectElevadorCriar && selectElevadorCriar.value === 'Sistema EMS') {
        const selecionados = select2Ems.val() || [];
        emsHidden.value = selecionados.join(',');
    }
    
    const formDataElevCriar = new FormData(form_os_criar);

    console.log(`urlElevCriarDestino: ${urlElevCriarDestino}`)

    try {
        const resposta = await fetch(urlElevCriarDestino, {
            method:'POST',
            body: formDataElevCriar,
            headers: {
                'X-CSRFToken': formDataElevCriar.get('csrfmiddlewaretoken')
            }
        });

        const dados = await resposta.json();
        if (resposta.ok && dados.sucesso) {
            await Swal.fire({
                title: "Sucesso!",
                text: "A Ordem de Serviço, foi salva com sucesso",
                icon: "success"
            })
            modal_os_criar.hide()
            window.location.reload()
        } else {
            console.log("Erros encontrados no formulário:", dados)
            modal_os_concluir.hide()
            Swal.fire("Erro!", "Não foi possível salvar. Verifique os dados inseridos", "error")
        }

    } catch (erro) {
        console.error("Erro critico na conexão: ", erro)
        alert("Erro ao conectar com o servidor. Tente novamente mais tarde.")
    }
});


form_os_concluir.addEventListener('submit', async function(evento_elev_concluir_os) {
    evento_elev_concluir_os.preventDefault();

    const urlElevConcluirDestino = form_os_concluir.action;
    console.log(urlElevConcluirDestino)
    const formDataElevConcluir = new FormData(form_os_concluir);

    try {
        const resposta = await fetch(urlElevConcluirDestino, {
            method:'POST',
            body: formDataElevConcluir,
            headers: {
                'X-CSRFToken': formDataElevConcluir.get('csrfmiddlewaretoken')
            }
        });

        const dados = await resposta.json();
        if (resposta.ok && dados.sucesso) {
            modal_os_concluir.hide();
            await Swal.fire({
                title: "Sucesso!",
                text: "A Ordem de Serviço foi salva com sucesso.",
                icon: "success"
            });
            window.location.reload();
        } else {
            console.log("Erros encontrados no formulário: ", dados);
            Swal.fire("Erro!", "Não foi possível salvar. Verifique os dados inseridos.", "error");
        }

    } catch (erro) {
        console.error("Erro critico na conexão: ", erro)
        alert("Erro ao conectar com o servidor. Tente novamente mais tarde.")
    }
});


// -------- NOVAS FUNÇÕES PARA OS MODAIS DE LISTA E VISUALIZAR --------

function abrirModalListaAbertasElev() {
    const modalLista = new bootstrap.Modal(document.getElementById('modal-lista-abertas-elev'));
    modalLista.show();
}

function abrirModalVisualizarElev(protocolo, data_hora, elevador, ocorrencia, aprisionamento, solicitante, atendente, status, parado, chegada, saida, tmpChegada, tmpSaida, tecnico, componente, subcomponente, servico, midia) {
    // Esconde o modal de lista se estiver aberto para não conflitar
    const modalListaEl = document.getElementById('modal-lista-abertas-elev');
    if (modalListaEl && modalListaEl.classList.contains('show')) {
        const modalLista = bootstrap.Modal.getInstance(modalListaEl);
        if (modalLista) modalLista.hide();
    }

    // Mídia
    const midiaSecao = document.getElementById('vis-elev-secao-midia');
    const previewBox = document.getElementById('vis-elev-midia-preview-box');
    const downloadBtn = document.getElementById('vis-elev-midia-download-btn');
    const filenameEl = document.getElementById('vis-elev-midia-filename');
    const typeEl = document.getElementById('vis-elev-midia-type');
    const iconEl = document.getElementById('vis-elev-midia-icon');
    
    if (midia) {
        midiaSecao.classList.remove('d-none');
        downloadBtn.href = midia;
        
        const fileName = midia.split('/').pop().split('?')[0];
        filenameEl.innerText = fileName;
        
        const ext = fileName.split('.').pop().toLowerCase();
        let iconClass = 'bi-file-earmark';
        let typeName = 'Arquivo';
        
        if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
            iconClass = 'bi-file-earmark-image';
            typeName = 'Imagem';
        } else if (['pdf'].includes(ext)) {
            iconClass = 'bi-file-earmark-pdf';
            typeName = 'Documento PDF';
        } else if (['doc', 'docx'].includes(ext)) {
            iconClass = 'bi-file-earmark-word';
            typeName = 'Documento Word';
        } else if (['mp4', 'webm', 'ogg'].includes(ext)) {
            iconClass = 'bi-file-earmark-play';
            typeName = 'Vídeo';
        }
        
        iconEl.innerHTML = `<i class="bi ${iconClass}"></i>`;
        typeEl.innerText = typeName;
        
        previewBox.onclick = function() {
            if (typeof window.openGenericFileViewer === 'function') {
                window.openGenericFileViewer(midia, fileName);
            } else {
                window.open(midia, '_blank');
            }
        };
    } else {
        midiaSecao.classList.add('d-none');
    }

    // Preenche os dados gerais
    document.getElementById('vis-elev-protocolo').innerText = protocolo || '-';
    document.getElementById('vis-elev-data').innerText = data_hora || '-';
    document.getElementById('vis-elev-elevador').innerText = elevador || '-';
    document.getElementById('vis-elev-ocorrencia').innerText = ocorrencia || '-';
    document.getElementById('vis-elev-aprisionamento').innerText = aprisionamento || '-';
    document.getElementById('vis-elev-solicitante').innerText = solicitante || '-';
    document.getElementById('vis-elev-atendente').innerText = atendente || '-';
    
    // Status visual
    const statusEl = document.getElementById('vis-elev-status');
    statusEl.innerHTML = '';
    if(status === 'ABERTA') {
        statusEl.innerHTML = '<span class="badge bg-warning">ABERTA</span>';
    } else if(status === 'CONCLUIDA' || status === 'CONCLUÍDA') {
        statusEl.innerHTML = '<span class="badge bg-success">CONCLUÍDA</span>';
    } else {
        statusEl.innerHTML = `<span class="badge bg-secondary">${status}</span>`;
    }

    document.getElementById('vis-elev-parado').innerText = parado || '-';

    // Preenche os dados de conclusão
    const secaoConclusaoTexto = document.getElementById('vis-elev-secao-conclusao-texto');
    const timelineChegada = document.getElementById('vis-elev-timeline-chegada');
    const timelineSaida = document.getElementById('vis-elev-timeline-saida');
    const containerTecnico = document.getElementById('vis-elev-container-tecnico');
    const secaoComponentes = document.getElementById('vis-elev-secao-componentes');
    
    if (status === 'CONCLUIDA' || status === 'CONCLUÍDA' || chegada) {
        if(secaoConclusaoTexto) secaoConclusaoTexto.classList.remove('d-none');
        if(timelineChegada) timelineChegada.classList.remove('d-none');
        if(timelineSaida) timelineSaida.classList.remove('d-none');
        if(containerTecnico) containerTecnico.classList.remove('d-none');
        if(secaoComponentes) secaoComponentes.classList.remove('d-none');
        
        document.getElementById('vis-elev-chegada').innerText = chegada || '-';
        document.getElementById('vis-elev-saida').innerText = saida || '-';
        document.getElementById('vis-elev-tmp-chegada').innerText = tmpChegada ? `(${tmpChegada} min)` : '';
        document.getElementById('vis-elev-tmp-saida').innerText = tmpSaida ? `(${tmpSaida} min)` : '';
        document.getElementById('vis-elev-tecnico').innerText = tecnico || '-';
        document.getElementById('vis-elev-componente').innerText = componente || '-';
        document.getElementById('vis-elev-subcomponente').innerText = subcomponente || '-';
        document.getElementById('vis-elev-servico').innerText = servico || '-';
    } else {
        if(secaoConclusaoTexto) secaoConclusaoTexto.classList.add('d-none');
        if(timelineChegada) timelineChegada.classList.add('d-none');
        if(timelineSaida) timelineSaida.classList.add('d-none');
        if(containerTecnico) containerTecnico.classList.add('d-none');
        if(secaoComponentes) secaoComponentes.classList.add('d-none');
    }

    const modalVis = new bootstrap.Modal(document.getElementById('modal-visualizar-os-elev'));
    modalVis.show();
}

// Inicializar a tabela do modal e o contador do widget quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    const tabelaModalEl = document.getElementById('tabela-elev-abertas-modal');
    if (tabelaModalEl) {
        // Conta as linhas para o widget
        const tbody = tabelaModalEl.querySelector('tbody');
        let countTrs = 0;
        if (tbody) {
            const trs = tbody.querySelectorAll('tr');
            countTrs = trs.length;
            // Ignora o tr de "nenhum encontrado" se houver apenas 1 td com colspan
            if (countTrs === 1 && trs[0].querySelector('td').colSpan > 1) {
                countTrs = 0;
            }
        }
        
        const alertaDashboard = document.getElementById('alerta-abertas-dashboard');
        const alertaCount = document.getElementById('alerta-abertas-count');
        const alertaLista = document.getElementById('alerta-abertas-lista');
        
        if (alertaDashboard && alertaCount) {
            alertaCount.innerText = countTrs;
            if (countTrs === 0) {
                // Muda para estado de sucesso (Tudo em ordem)
                alertaDashboard.classList.remove('border-danger');
                alertaDashboard.classList.add('border-success');
                
                const header = alertaDashboard.querySelector('.card-header');
                if (header) {
                    header.classList.remove('bg-danger');
                    header.classList.add('bg-success');
                    header.innerHTML = `<h6 class="mb-0 fw-bold" style="font-size: 0.95rem; letter-spacing: 0.5px;"><i class="bi bi-check-circle-fill me-2"></i> Tudo em ordem! Nenhuma O.S Aberta</h6><span class="badge bg-white text-success rounded-pill fs-6 px-3 shadow-sm">0</span>`;
                }
                
                const btn = alertaDashboard.querySelector('button');
                if (btn) {
                    btn.classList.remove('btn-danger');
                    btn.classList.add('btn-success');
                    btn.disabled = true;
                    btn.innerHTML = `<i class="bi bi-check2-all me-2 fs-5"></i> NENHUMA PENDÊNCIA NO MOMENTO`;
                }
                
                if (alertaLista) {
                    alertaLista.innerHTML = `<div class="list-group-item py-4 text-center text-success bg-success bg-opacity-10 fw-semibold border-success-subtle"><i class="bi bi-emoji-smile fs-3 d-block mb-2"></i> Parabéns! Nenhuma manutenção aguardando atendimento.</div>`;
                }
            }
        }

        // Inicializa DataTable
        if (typeof DataTable !== 'undefined') {
            new DataTable(tabelaModalEl, {
                responsive: true,
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
                    aplicarFiltroColunasModal(this.api());
                }
            });
        }
    }
});

