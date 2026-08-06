
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || "";

async function loadMPMTable() {
    try {
        const response = await fetch("/elevadores/api/manutencao_preventiva/");
        if (!response.ok) throw new Error("Falha ao buscar MPM");
        const data = await response.json();
        const lista = Array.isArray(data) ? data : (data.results || []);
        
        const tabelaEl = $('#tabela-mpm-dados');
        if ($.fn.DataTable.isDataTable(tabelaEl)) {
            tabelaEl.DataTable().destroy();
        }

        const tbody = document.getElementById("mpm-tbody");
        if (!tbody) return;
        tbody.innerHTML = "";
        
        const meses = {
            '01': 'JAN', '02': 'FEV', '03': 'MAR', '04': 'ABR',
            '05': 'MAI', '06': 'JUN', '07': 'JUL', '08': 'AGO',
            '09': 'SET', '10': 'OUT', '11': 'NOV', '12': 'DEZ'
        };

        const formatData = (dateStr) => {
            if (!dateStr || dateStr === 'null') return 'N/A';
            const p = dateStr.split('-');
            if (p.length === 3) return `${p[2]}/${p[1]}/${p[0]}`;
            return dateStr;
        };

        lista.forEach(item => {
            let mesRefFormatado = item.mes_referencia;
            let dataPrevista = '-';
            let mesRefSort = item.mes_referencia;
            if (item.mes_referencia && item.mes_referencia.includes('-')) {
                const parts = item.mes_referencia.split('-');
                if (parts.length >= 2) {
                    const ano = parts[0];
                    const mes = parts[1];
                    mesRefFormatado = `${meses[mes] || mes}/${ano}`;
                    dataPrevista = `10/${mes}/${ano}`;
                }
            }

            // Extract number from elevador for sorting
            const match = item.elevador ? String(item.elevador).match(/\d+/) : null;
            const elevNum = match ? parseInt(match[0], 10) : 999;

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${item.ordem_servico || "-"}</td>
                <td data-order="${elevNum}">${item.elevador || "-"}</td>
                <td data-order="${mesRefSort}">${mesRefFormatado}</td>
                <td>${dataPrevista}</td>
                <td>${formatData(item.data_execucao)}</td>
                <td>${item.tecnico || "N/A"}</td>
                <td><span class="badge bg-${item.status === "EXECUTADO" ? "success" : "danger"}">${item.status}</span></td>
                <td>
                    <div class="d-flex flex-nowrap justify-content-center gap-1">
                        <button class="btn btn-sm btn-outline-primary" onclick="abrirVisualizarMPM('${encodeURIComponent(JSON.stringify(item))}')" title="Visualizar">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" onclick="editarMPM(${item.id})" title="Editar"><i class="bi bi-pencil"></i></button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteMPM(${item.id})" title="Excluir"><i class="bi bi-trash"></i></button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
        
        if (typeof DataTable !== 'undefined') {
            new DataTable(tabelaEl[0], {
                language: { url: 'https://cdn.datatables.net/plug-ins/2.0.3/i18n/pt-BR.json' },
                pageLength: 14,
                order: [[2, 'desc'], [1, 'asc']] // Ordem por mês decrescente (coluna 2), e elevador crescente (coluna 1)
            });
        }
    } catch (error) {
        console.error("Erro ao carregar MPM:", error);
    }
}

async function loadPecasTable() {
    try {
        const response = await fetch("/elevadores/api/peca_manutencao/");
        if (!response.ok) throw new Error("Falha ao buscar Peças");
        const data = await response.json();
        const lista = Array.isArray(data) ? data : (data.results || []);
        
        const tabelaEl = $('#tabela-pecas-dados');
        if ($.fn.DataTable.isDataTable(tabelaEl)) {
            tabelaEl.DataTable().destroy();
        }
        
        const tbody = document.getElementById("pecas-tbody");
        if (!tbody) return;
        tbody.innerHTML = "";
        
        const formatData = (dateStr) => {
            if (!dateStr || dateStr === 'null') return '-';
            const p = dateStr.split('-');
            if (p.length === 3) return `${p[2]}/${p[1]}/${p[0]}`;
            return dateStr;
        };

        lista.forEach(item => {
            const isSub = item.status === "SUBSTITUIDA";
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${formatData(item.data_registro)}</td>
                <td>${item.elevador}</td>
                <td>${item.tipo_peca}</td>
                <td>${formatData(item.data_previsao_troca)}</td>
                <td><span class="badge bg-${isSub ? "success" : "warning text-dark"}">${item.status}</span></td>
                <td class="text-danger fw-bold elev-timer text-nowrap" data-start="${isSub ? '' : (item.created_at || item.data_registro || '')}">${isSub ? '-' : 'Calculando...'}</td>
                <td>
                    <div class="d-flex flex-nowrap justify-content-center gap-1">
                        <button class="btn btn-sm btn-outline-primary" onclick="abrirVisualizarPeca('${encodeURIComponent(JSON.stringify(item))}')" title="Visualizar"><i class="bi bi-eye"></i></button>
                        ${(!item.ordem_servico && item.status === 'PENDENTE') ? `<button class="btn btn-sm btn-success text-white fw-bold shadow-sm" onclick="openConcluirModal(${item.id})" title="Concluir Troca"><i class="bi bi-check2-circle"></i></button>` : ''}
                        <button class="btn btn-sm btn-outline-warning" onclick="editarPeca(${item.id})" title="Editar"><i class="bi bi-pencil"></i></button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deletePeca(${item.id})" title="Excluir"><i class="bi bi-trash"></i></button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
        
        if (typeof DataTable !== 'undefined') {
            new DataTable(tabelaEl[0], {
                language: { url: 'https://cdn.datatables.net/plug-ins/2.0.3/i18n/pt-BR.json' },
                order: [[0, 'desc']] // Ordem por data registro (agora na coluna 0)
            });
        }
        if (typeof iniciarTimersGlobais === 'function') iniciarTimersGlobais();
    } catch (error) {
        console.error("Erro ao carregar Peças:", error);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadMPMTable();
    loadPecasTable();
    carregarContratosSelect();

    function carregarContratosSelect() {
        const selects = document.querySelectorAll("#mpmContrato, #editMpmContrato");
        if (selects.length === 0) return;
        
        // Busca apenas contratos vinculados ao app de Elevadores
        fetch("/contratos/api/contratos/?categoria=ELEVADORES")
            .then(res => res.json())
            .then(data => {
                const lista = Array.isArray(data) ? data : (data.results || []);
                let optionsHtml = '<option value="" selected>Selecione um contrato...</option>';
                lista.forEach(c => {
                    const label = `${c.num_contrato} - ${c.empresa_nome || 'Empresa'}`;
                    optionsHtml += `<option value="${c.id}">${label}</option>`;
                });
                selects.forEach(select => {
                    select.innerHTML = optionsHtml;
                    // Auto-seleciona o primeiro contrato de elevadores se houver apenas um
                    if (lista.length === 1) {
                        select.value = lista[0].id;
                    }
                });
            })
            .catch(err => console.error("Erro ao carregar contratos:", err));
    }

    // Auto-preencher mês de referência com o mês corrente
    const mpmMesReferenciaInput = document.getElementById("mpmMesReferencia");
    if (mpmMesReferenciaInput && !mpmMesReferenciaInput.value) {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        mpmMesReferenciaInput.value = `${year}-${month}`;
    }

    // Submit Cadastro MPM
    const formMPM = document.getElementById("formCadastroMPM");
    if (formMPM) {
        formMPM.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const btnSubmit = document.getElementById("btnSubmitFormCadastroMPM");
            if (btnSubmit) {
                btnSubmit.disabled = true;
                btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';
            }

            const formDataBase = new FormData(formMPM);
            let mesRef = formDataBase.get("mes_referencia");
            if (mesRef && mesRef.length === 7) {
                formDataBase.set("mes_referencia", mesRef + "-01");
            }
            
            // Build JSON payload
            const payload = {};
            for (let [key, val] of Array.from(formDataBase.entries())) {
                if (val !== "" && val !== null && val !== "null") {
                    payload[key] = val;
                }
            }
            payload['status'] = 'PENDENTE';
            
            const elevadores_registrados = [];
            const elevadorItems = document.querySelectorAll('.mpm-elevador-item');
            if (elevadorItems.length === 0) {
                if (typeof Swal !== 'undefined') Swal.fire('Atenção', 'Adicione pelo menos um elevador.', 'warning');
                else alert('Adicione pelo menos um elevador.');
                if (btnSubmit) { btnSubmit.disabled = false; btnSubmit.innerHTML = '<i class="bi bi-check-lg me-2"></i> Registrar Relatório MPM'; }
                return;
            }

            for (const item of elevadorItems) {
                const elevador = item.querySelector('.mpm-elevador').value;
                if (!elevador) continue;
                
                const situacao = item.querySelector('.mpm-situacao').value;
                const hora_inicio = item.querySelector('.mpm-hora-inicio').value;
                const hora_fim = item.querySelector('.mpm-hora-fim').value;

                elevadores_registrados.push({
                    elevador: elevador,
                    situacao: situacao,
                    hora_inicio: hora_inicio || null,
                    hora_fim: hora_fim || null
                });
            }
            
            if (elevadores_registrados.length === 0) {
                if (typeof Swal !== 'undefined') Swal.fire('Atenção', 'Nenhum elevador válido foi adicionado.', 'warning');
                if (btnSubmit) { btnSubmit.disabled = false; btnSubmit.innerHTML = '<i class="bi bi-check-lg me-2"></i> Registrar Relatório MPM'; }
                return;
            }
            
            payload['elevadores_registrados'] = elevadores_registrados;

            try {
                const res = await fetch("/elevadores/api/manutencao_preventiva/", {
                    method: "POST",
                    headers: { 
                        "X-CSRFToken": csrftoken,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });
                
                if (btnSubmit) { btnSubmit.disabled = false; btnSubmit.innerHTML = '<i class="bi bi-check-lg me-2"></i> Registrar Relatório MPM'; }
                
                if (res.ok) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById("modalCadastroMPM"));
                    if(modal) modal.hide();
                    formMPM.reset();
                    document.getElementById('mpmElevadoresContainer').innerHTML = '';
                    adicionarElevadorVazio();
                    loadMPMTable();
                    if(typeof Swal !== 'undefined') Swal.fire('Sucesso', 'MPM registrada com sucesso! Aguardando OS.', 'success');
                } else {
                    const errorData = await res.json();
                    console.error("Erro na API:", errorData);
                    if(typeof Swal !== 'undefined') Swal.fire('Erro', 'Falha ao salvar. Verifique os dados e tente novamente.', 'error');
                    else alert("Falha ao salvar. Verifique o console.");
                }
            } catch (err) {
                console.error("Falha na rede", err);
                if (btnSubmit) { btnSubmit.disabled = false; btnSubmit.innerHTML = '<i class="bi bi-check-lg me-2"></i> Registrar Relatório MPM'; }
                if(typeof Swal !== 'undefined') Swal.fire('Erro', 'Erro de conexão.', 'error');
            }
        });
    }

    // Submit Edit MPM
    const formEditarMPM = document.getElementById("formEditarMpm");
    if (formEditarMPM) {
        formEditarMPM.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const formData = new FormData(formEditarMPM);
            const id = formData.get("id") || document.getElementById('editMpmId').value;
            let mesRef = formData.get("mes_referencia");
            if (mesRef && mesRef.length === 7) {
                formData.set("mes_referencia", mesRef + "-01");
            }
            
            const payload = {};
            for (let [key, val] of Array.from(formData.entries())) {
                if (val !== "" && val !== null && val !== "null") {
                    payload[key] = val;
                }
            }
            
            const elevadores_registrados = [];
            const elevadorItems = document.querySelectorAll('#editMpmElevadoresContainer .mpm-elevador-item');
            if (elevadorItems.length === 0) {
                if (typeof Swal !== 'undefined') Swal.fire('Atenção', 'Adicione pelo menos um elevador.', 'warning');
                else alert('Adicione pelo menos um elevador.');
                return;
            }

            for (const item of elevadorItems) {
                const elevador = item.querySelector('.mpm-elevador').value;
                if (!elevador) continue;
                
                const situacao = item.querySelector('.mpm-situacao').value;
                const hora_inicio = item.querySelector('.mpm-hora-inicio').value;
                const hora_fim = item.querySelector('.mpm-hora-fim').value;

                elevadores_registrados.push({
                    elevador: elevador,
                    situacao: situacao,
                    hora_inicio: hora_inicio || null,
                    hora_fim: hora_fim || null
                });
            }
            
            if (elevadores_registrados.length === 0) {
                if (typeof Swal !== 'undefined') Swal.fire('Atenção', 'Nenhum elevador válido foi adicionado.', 'warning');
                return;
            }
            
            payload['elevadores_registrados'] = elevadores_registrados;

            try {
                const res = await fetch(`/elevadores/api/manutencao_preventiva/${id}/`, {
                    method: "PATCH",
                    headers: { 
                        "X-CSRFToken": csrftoken,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById("modalEditarMPM"));
                    if(modal) modal.hide();
                    formEditarMPM.reset();
                    loadMPMTable();
                    if(typeof Swal !== 'undefined') Swal.fire('Sucesso', 'MPM atualizada com sucesso!', 'success');
                } else {
                    const errorData = await res.json();
                    console.error("Erro na API:", errorData);
                    alert("Erro ao atualizar MPM. Verifique o console.");
                }
            } catch (err) { console.error(err); }
        });
    }

    // Submit Cadastro Peça
    const formPeca = document.getElementById("formCadastroPeca");
    if (formPeca) {
        formPeca.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const formData = new FormData(formPeca);
            // Append explicit fields if needed, but they should be correctly named in the HTML
            // Wait, does the HTML have name attributes for all inputs?
            // Let's manually append them if they don't have name attributes or map them
            formData.set('elevador', document.getElementById("pecaElevador").value);
            formData.set('andar', document.getElementById("pecaAndar").value);
            formData.set('tipo_peca', document.getElementById("pecaTipo").value);
            formData.set('data_previsao_troca', document.getElementById("pecaPrevisao").value);
            if (document.getElementById("pecaOS")) formData.set('ordem_servico', document.getElementById("pecaOS").value);
            if (document.getElementById("pecaTecnicoIdentificador")) formData.set('tecnico_identificador', document.getElementById("pecaTecnicoIdentificador").value);
            formData.set('status', 'PENDENTE');

            for (let [key, val] of Array.from(formData.entries())) {
                if (val === "" || val === null || val === "null" || (val instanceof File && val.size === 0)) {
                    formData.delete(key);
                }
            }

            try {
                const res = await fetch("/elevadores/api/peca_manutencao/", {
                    method: "POST",
                    headers: { "X-CSRFToken": csrftoken },
                    body: formData
                });
                if (res.ok) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById("modalCadastroPeca"));
                    modal.hide();
                    formPeca.reset();
                    loadPecasTable();
                } else {
                    alert("Erro ao salvar Peça");
                }
            } catch (err) { console.error(err); }
        });
    }

    // Submit Concluir Troca
    const formConcluir = document.getElementById("formConcluirTroca");
    if (formConcluir) {
        formConcluir.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("concluirPecaId").value;
            const payload = {
                tecnico: document.getElementById("concluirTecnico").value,
                data_efetiva_troca: document.getElementById("concluirData").value,
                status: "SUBSTITUIDA"
            };

            try {
                const res = await fetch(`/elevadores/api/peca_manutencao/${id}/`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById("modalConcluirTroca"));
                    modal.hide();
                    formConcluir.reset();
                    loadPecasTable();
                } else {
                    alert("Erro ao concluir troca");
                }
            } catch (err) { console.error(err); }
        });
    }
});

window.openConcluirModal = function(id) {
    document.getElementById("concluirPecaId").value = id;
    const modal = new bootstrap.Modal(document.getElementById("modalConcluirTroca"));
    modal.show();
}

window.abrirVisualizarPeca = function(pecaStrEncoded) {
    try {
        const item = JSON.parse(decodeURIComponent(pecaStrEncoded));
        document.getElementById('view_peca_elevador').textContent = item.elevador || '-';
        document.getElementById('view_peca_andar').textContent = item.andar || '-';
        document.getElementById('view_peca_nome').textContent = item.tipo_peca || '-';
        document.getElementById('view_peca_qtd').textContent = item.quantidade || '1';
        
        const fmtDate = (d) => {
            if (!d) return '-';
            const p = d.split('-');
            return p.length === 3 ? `${p[2]}/${p[1]}/${p[0]}` : d;
        };

        document.getElementById('view_peca_data_registro').textContent = fmtDate(item.data_registro);
        document.getElementById('view_peca_previsao').textContent = fmtDate(item.data_previsao_troca);
        document.getElementById('view_peca_tec_identificador').textContent = item.tecnico_identificador || '-';
        
        document.getElementById('view_peca_data_efetiva').textContent = fmtDate(item.data_efetiva_troca);
        document.getElementById('view_peca_tecnico').textContent = item.tecnico || '-';
        
        document.getElementById('view_peca_status').textContent = item.status || '-';
        document.getElementById('view_peca_status').className = 'badge bg-' + (item.status === 'SUBSTITUIDA' ? 'success' : 'warning text-dark');
        
        document.getElementById('view_peca_os').textContent = item.ordem_servico || '-';

        const midiaSecao = document.getElementById('vis_peca_secao_midia');
        const previewBox = document.getElementById('vis_peca_midia_preview_box');
        const downloadBtn = document.getElementById('vis_peca_midia_download-btn'); // Typo in ID matching
        const filenameEl = document.getElementById('vis_peca_midia_filename');
        const typeEl = document.getElementById('vis_peca_midia_type');
        const iconEl = document.getElementById('vis_peca_midia_icon');
        
        if (item.midia) {
            midiaSecao.classList.remove('d-none');
            // Ensure ID is matched correctly
            if(document.getElementById('vis_peca_midia_download_btn')) {
                document.getElementById('vis_peca_midia_download_btn').href = item.midia;
            }
            
            const fileName = item.midia.split('/').pop().split('?')[0];
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
                    window.openGenericFileViewer(item.midia, fileName);
                } else {
                    window.open(item.midia, '_blank');
                }
            };
        } else {
            midiaSecao.classList.add('d-none');
        }

        const myModal = new bootstrap.Modal(document.getElementById('modalVisualizarPeca'));
        myModal.show();
    } catch (e) { console.error(e); }
}

window.editarPeca = async function(id) {
    if (!window.userCanEditElevadores) {
        if (typeof Swal !== 'undefined') Swal.fire('Acesso Negado', 'Você não tem permissão para editar registros. Apenas supervisores podem realizar esta ação.', 'error');
        else alert('Acesso Negado: Apenas supervisores podem editar.');
        return;
    }
    try {
        const response = await fetch(`/elevadores/api/peca_manutencao/${id}/`);
        if (!response.ok) throw new Error('Erro ao buscar dados da Peça');
        const peca = await response.json();

        document.getElementById('editPecaId').value = peca.id || id;
        document.getElementById('editPecaElevador').value = peca.elevador || '';
        document.getElementById('editPecaAndar').value = peca.andar || '';
        document.getElementById('editPecaOS').value = peca.ordem_servico || '';
        document.getElementById('editPecaTipo').value = peca.tipo_peca || '';
        document.getElementById('editPecaTecnicoIdentificador').value = peca.tecnico_identificador || '';
        document.getElementById('editPecaRegistro').value = peca.data_registro || '';
        document.getElementById('editPecaPrevisao').value = peca.data_previsao_troca || '';
        document.getElementById('editPecaStatus').value = peca.status || 'PENDENTE';
        document.getElementById('editPecaEfetiva').value = peca.data_efetiva_troca || '';
        document.getElementById('editPecaTecnico').value = peca.tecnico || '';

        const modal = new bootstrap.Modal(document.getElementById('modalEditarPeca'));
        modal.show();
    } catch (e) {
        console.error(e);
        if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Não foi possível carregar os dados da Peça.', 'error');
    }
}

// Intercepta Form Editar Peça
document.addEventListener("DOMContentLoaded", () => {
    const formEditarPeca = document.getElementById("formEditarPeca");
    if (formEditarPeca) {
        formEditarPeca.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("editPecaId").value;
            
            const formData = new FormData(formEditarPeca);
            formData.set('elevador', document.getElementById("editPecaElevador").value);
            formData.set('andar', document.getElementById("editPecaAndar").value);
            formData.set('ordem_servico', document.getElementById("editPecaOS").value);
            formData.set('tipo_peca', document.getElementById("editPecaTipo").value);
            formData.set('tecnico_identificador', document.getElementById("editPecaTecnicoIdentificador").value);
            formData.set('data_registro', document.getElementById("editPecaRegistro").value);
            formData.set('data_previsao_troca', document.getElementById("editPecaPrevisao").value);
            formData.set('status', document.getElementById("editPecaStatus").value);
            formData.set('data_efetiva_troca', document.getElementById("editPecaEfetiva").value);
            formData.set('tecnico', document.getElementById("editPecaTecnico").value);

            for (let [key, val] of Array.from(formData.entries())) {
                if (val === "" || val === null || val === "null" || (val instanceof File && val.size === 0)) {
                    formData.delete(key);
                }
            }

            try {
                const res = await fetch(`/elevadores/api/peca_manutencao/${id}/`, {
                    method: "PATCH",
                    headers: { 
                        "X-CSRFToken": csrftoken 
                    },
                    body: formData
                });
                if (res.ok) {
                    bootstrap.Modal.getInstance(document.getElementById("modalEditarPeca")).hide();
                    loadPecasTable();
                    if (typeof Swal !== 'undefined') Swal.fire('Sucesso!', 'Peça atualizada com sucesso.', 'success');
                } else {
                    alert('Erro ao editar Peça');
                }
            } catch (err) { console.error(err); }
        });
    }
});

window.deleteMPM = async function(id) {
    if (!window.userCanEditElevadores) {
        if (typeof Swal !== 'undefined') Swal.fire('Acesso Negado', 'Você não tem permissão para excluir registros de MPM. Apenas supervisores podem realizar esta ação.', 'error');
        else alert('Acesso Negado: Apenas supervisores podem excluir.');
        return;
    }

    if (typeof Swal !== 'undefined') {
        const result = await Swal.fire({
            title: 'Tem certeza?',
            text: "Deseja realmente apagar este registro MPM? Esta ação não pode ser desfeita.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sim, excluir!',
            cancelButtonText: 'Cancelar'
        });
        if (!result.isConfirmed) return;
    } else {
        if(!confirm("Deseja realmente apagar este registro MPM?")) return;
    }

    try {
        const res = await fetch(`/elevadores/api/manutencao_preventiva/${id}/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": csrftoken }
        });
        if (res.ok) {
            loadMPMTable();
            if (typeof Swal !== 'undefined') Swal.fire('Excluído!', 'Registro de MPM apagado com sucesso.', 'success');
        } else {
            if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Ocorreu um problema ao excluir a MPM.', 'error');
            else alert('Erro ao excluir MPM');
        }
    } catch(e) { console.error(e); }
}

window.editarMPM = async function(id) {
    if (!window.userCanEditElevadores) {
        if (typeof Swal !== 'undefined') Swal.fire('Acesso Negado', 'Você não tem permissão para editar registros. Apenas supervisores podem realizar esta ação.', 'error');
        else alert('Acesso Negado: Apenas supervisores podem editar.');
        return;
    }
    try {
        const modalEl = document.getElementById('modalEditarMPM');
        // Usar bootstrap global ou construtor
        let modal = bootstrap.Modal.getInstance(modalEl);
        if (!modal) modal = new bootstrap.Modal(modalEl);
        modal.show();

        const loadingInfo = document.getElementById('editMpmLoadingInfo');
        const formContent = document.getElementById('editMpmFormContent');
        if (loadingInfo) loadingInfo.classList.remove('d-none');
        if (formContent) formContent.classList.add('d-none');

        const response = await fetch(`/elevadores/api/manutencao_preventiva/${id}/`);
        if (!response.ok) throw new Error('Erro ao buscar dados da MPM');
        const mpm = await response.json();

        const setValAndTrigger = (id, val) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.value = val;
            if (window.jQuery && $(el).hasClass('select2-hidden-accessible')) {
                $(el).trigger('change.select2');
            }
            el.dispatchEvent(new Event('change'));
        };

        document.getElementById('editMpmId').value = mpm.id || id;
        setValAndTrigger('editMpmContrato', mpm.contrato || '');
        document.getElementById('editMpmMes').value = mpm.mes_referencia ? mpm.mes_referencia.substring(0, 7) : '';
        document.getElementById('editMpmDescricaoServico').value = mpm.descricao_servico || '';
        
        setValAndTrigger('editMpmTecnicoNome', mpm.tecnico || '');
        document.getElementById('editMpmDataExecucao').value = mpm.data_execucao || '';
        document.getElementById('editMpmHoraChegada').value = mpm.hora_chegada ? mpm.hora_chegada.substring(0, 5) : '';
        document.getElementById('editMpmHoraSaida').value = mpm.hora_saida ? mpm.hora_saida.substring(0, 5) : '';
        
        setValAndTrigger('editMpmClienteNome', mpm.cliente_nome || '');
        
        // Load multiple elevators
        const editContainer = document.getElementById('editMpmElevadoresContainer');
        if (editContainer) {
            editContainer.innerHTML = ''; // clear previous
            if (mpm.elevadores_registrados && mpm.elevadores_registrados.length > 0) {
                mpm.elevadores_registrados.forEach(el => {
                    adicionarElevador('editMpmElevadoresContainer', el);
                });
            } else {
                adicionarElevador('editMpmElevadoresContainer');
            }
        }

        if (loadingInfo) loadingInfo.classList.add('d-none');
        if (formContent) formContent.classList.remove('d-none');
        
    } catch (e) {
        console.error(e);
        if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Não foi possível carregar os dados da MPM.', 'error');
        else alert('Erro ao carregar dados da MPM');
    }
}

window.deletePeca = async function(id) {
    if (!window.userCanEditElevadores) {
        if (typeof Swal !== 'undefined') Swal.fire('Acesso Negado', 'Você não tem permissão para excluir peças. Apenas supervisores podem realizar esta ação.', 'error');
        else alert('Acesso Negado: Apenas supervisores podem excluir.');
        return;
    }
    
    if (typeof Swal !== 'undefined') {
        const result = await Swal.fire({
            title: 'Tem certeza?',
            text: "Deseja realmente apagar esta peça? Esta ação não pode ser desfeita.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sim, excluir!',
            cancelButtonText: 'Cancelar'
        });
        if (!result.isConfirmed) return;
    } else {
        if(!confirm("Deseja realmente apagar esta peça?")) return;
    }

    try {
        const res = await fetch(`/elevadores/api/peca_manutencao/${id}/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": csrftoken }
        });
        if (res.ok) {
            loadPecasTable();
            if (typeof Swal !== 'undefined') Swal.fire('Excluída!', 'Peça apagada com sucesso.', 'success');
        } else {
            if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Ocorreu um problema ao excluir a Peça.', 'error');
            else alert('Erro ao excluir Peça');
        }
    } catch(e) { console.error(e); }
}

window.abrirVisualizarMPM = function(mpmStrEncoded) {
    const data = JSON.parse(decodeURIComponent(mpmStrEncoded));
    
    document.getElementById('vis-mpm-mes').innerText = data.mes_referencia ? data.mes_referencia.substring(0, 7) : '-';
    document.getElementById('vis-mpm-elevador').innerText = data.elevador || '-';
    document.getElementById('vis-mpm-situacao').innerText = data.situacao_equipamento || data.status || '-';
    document.getElementById('vis-mpm-descricao').innerText = data.descricao_servico || '-';
    document.getElementById('vis-mpm-observacao').innerText = data.observacao || '-';
    
    // Foto
    const fotoContainer = document.getElementById('vis-mpm-foto-container');
    const fotoImg = document.getElementById('vis-mpm-foto');
    if (data.foto_poco) {
        fotoImg.src = data.foto_poco;
        fotoContainer.style.display = 'block';
    } else {
        fotoImg.src = '';
        fotoContainer.style.display = 'none';
    }
    
    // Envolvidos
    document.getElementById('vis-mpm-tecnico-nome').innerText = data.tecnico || '-';
    document.getElementById('vis-mpm-tecnico-chapa').innerText = data.tecnico_chapa || 'Chapa não informada';
    document.getElementById('vis-mpm-data-exec').innerText = data.data_execucao ? data.data_execucao.split('-').reverse().join('/') : '-';
    document.getElementById('vis-mpm-hora-chegada').innerText = data.hora_chegada ? data.hora_chegada.substring(0, 5) : '-';
    document.getElementById('vis-mpm-hora-saida').innerText = data.hora_saida ? data.hora_saida.substring(0, 5) : '-';
    
    // Visto
    document.getElementById('vis-mpm-cliente-nome').innerText = data.cliente_nome || '-';
    document.getElementById('vis-mpm-cliente-email').innerText = data.cliente_email || '-';
    document.getElementById('vis-mpm-cliente-comentarios').innerText = data.cliente_comentarios || '-';
    document.getElementById('vis-mpm-cliente-data').innerText = data.cliente_data ? data.cliente_data.split('-').reverse().join('/') : '-';

    const midiaSecao = document.getElementById('vis-mpm-secao-midia');
    const previewBox = document.getElementById('vis-mpm-midia-preview-box');
    const downloadBtn = document.getElementById('vis-mpm-midia-download-btn');
    const filenameEl = document.getElementById('vis-mpm-midia-filename');
    const typeEl = document.getElementById('vis-mpm-midia-type');
    const iconEl = document.getElementById('vis-mpm-midia-icon');
    
    if (data.midia) {
        midiaSecao.classList.remove('d-none');
        downloadBtn.href = data.midia;
        
        const fileName = data.midia.split('/').pop().split('?')[0];
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
                window.openGenericFileViewer(data.midia, fileName);
            } else {
                window.open(data.midia, '_blank');
            }
        };
    } else {
        midiaSecao.classList.add('d-none');
    }
    
    const m = new bootstrap.Modal(document.getElementById('modal-visualizar-mpm'));
    m.show();
}


// Bloco de carregamento de contatos duplicado removido. A inicialização real ocorre na função carregarContatosMPMCliente.

// --- LOGIC FOR MULTIPLE ELEVATORS ---
function adicionarElevadorVazio() {
    adicionarElevador();
}

function adicionarElevador(containerId = 'mpmElevadoresContainer', data = null) {
    const container = document.getElementById(containerId);
    const template = document.getElementById('mpmElevadorTemplate');
    if (!container || !template) return;
    
    const clone = template.content.cloneNode(true);
    const item = clone.querySelector('.mpm-elevador-item');
    
    if (data) {
        const selElevador = item.querySelector('.mpm-elevador');
        if (selElevador && data.elevador) selElevador.value = data.elevador;
        const selSituacao = item.querySelector('.mpm-situacao');
        if (selSituacao && data.situacao) selSituacao.value = data.situacao;
        const inputIni = item.querySelector('.mpm-hora-inicio');
        if (inputIni && data.hora_inicio) inputIni.value = data.hora_inicio.substring(0, 5);
        const inputFim = item.querySelector('.mpm-hora-fim');
        if (inputFim && data.hora_fim) inputFim.value = data.hora_fim.substring(0, 5);
    }
    
    // Add remove event listener
    const btnRemove = item.querySelector('.btn-remover-elevador');
    btnRemove.addEventListener('click', () => {
        item.remove();
        if (container.children.length === 0) {
            adicionarElevador(containerId); // Always keep at least one
        }
    });

    container.appendChild(item);
}

document.addEventListener("DOMContentLoaded", () => {
    const btnAdd = document.getElementById('btnAddElevadorMPM');
    if (btnAdd) {
        btnAdd.addEventListener('click', () => adicionarElevador('mpmElevadoresContainer'));
    }
    const btnAddEdit = document.getElementById('btnAddElevadorEditMPM');
    if (btnAddEdit) {
        btnAddEdit.addEventListener('click', () => adicionarElevador('editMpmElevadoresContainer'));
    }
    
    // Initialize first elevator block if modal exists
    const modalRegistrar = document.getElementById('modalCadastroMPM');
    if (modalRegistrar) {
        modalRegistrar.addEventListener('show.bs.modal', () => {
            const container = document.getElementById('mpmElevadoresContainer');
            if (container && container.children.length === 0) {
                adicionarElevadorVazio();
            }
        });
    }

    // Auto-fill dates when Technician is selected
    const selectsTecnicos = document.querySelectorAll('#mpmTecnicoNome, #editMpmTecnicoNome');
    selectsTecnicos.forEach(selectTecnico => {
        selectTecnico.addEventListener('change', (e) => {
            const isEdit = selectTecnico.id === 'editMpmTecnicoNome';
            const prefix = isEdit ? 'editMpm' : 'mpm';
            
            // Find option and get chapa
            const opt = selectTecnico.options[selectTecnico.selectedIndex];
            if (opt && opt.dataset.chapa) {
                // document.getElementById(`${prefix}TecnicoChapa`).value = opt.dataset.chapa;
            }
            
            // Auto fill current date and time if empty
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            
            const dataExec = document.getElementById(`${prefix}DataExecucao`);
            const horaCheg = document.getElementById(`${prefix}HoraChegada`);
            const horaSaida = document.getElementById(`${prefix}HoraSaida`);
            const dataCli = document.getElementById(`${prefix}ClienteData`);
            
            if (dataExec && !dataExec.value) dataExec.value = `${year}-${month}-${day}`;
            if (horaCheg && !horaCheg.value) horaCheg.value = `${hours}:${minutes}`;
            if (horaSaida && !horaSaida.value) horaSaida.value = `${hours}:${minutes}`;
            if (dataCli && !dataCli.value) dataCli.value = `${year}-${month}-${day}`;
        });
    });
    
    // Fetch predial contacts for Cliente
    carregarContatosMPMCliente();
});

function carregarContatosMPMCliente() {
    const selectsClientes = document.querySelectorAll('#mpmClienteNome, #editMpmClienteNome');
    if (selectsClientes.length === 0) return;
    
    fetch('/empresas/api/contatos_por_app/?app=MANUTENCAO_PREDIAL')
        .then(res => res.json())
        .then(contatos => {
            selectsClientes.forEach(selectCliente => {
                const isEdit = selectCliente.id === 'editMpmClienteNome';
                const prefix = isEdit ? 'editMpm' : 'mpm';
                
                const firstOption = selectCliente.querySelector('option[value=""]');
                selectCliente.innerHTML = '';
                if (firstOption) selectCliente.appendChild(firstOption);
                else selectCliente.innerHTML = '<option value="">Nenhum / Não Informado</option>';

                const loggedUser = selectCliente.getAttribute('data-logged-user');

                if (Array.isArray(contatos)) {
                    contatos.forEach(c => {
                        // Adiciona apenas fiscais e tecnicos prediais
                        const cargo = (c.cargo || "").toLowerCase();
                        if (cargo.includes("fiscal") || cargo.includes("téc") || cargo.includes("tec")) {
                            const opt = document.createElement('option');
                            opt.value = `${c.nome} - ${c.cargo}`;
                            opt.textContent = `${c.nome} - ${c.cargo}`;
                            opt.dataset.email = c.email || '';
                            
                            // Select if matches logged user
                            if (loggedUser && opt.value.toLowerCase().includes(loggedUser.toLowerCase().trim())) {
                                opt.selected = true;
                            }
                            
                            selectCliente.appendChild(opt);
                        }
                    });
                }
                
                // Listen for changes
                selectCliente.addEventListener('change', (e) => {
                    // Do nothing for now
                });
                // Initialize Select2 after populating options
                if (window.jQuery && $(selectCliente).length) {
                    $(selectCliente).select2({
                        theme: 'bootstrap-5',
                        width: '100%',
                        tags: true,
                        dropdownParent: $(selectCliente).closest('.modal')
                    });
                }
            });
        })
        .catch(err => console.error("Erro carregar contatos predial MPM:", err));
}

// Concluir MPM logic
window.openConcluirModal = function(id, mes_referencia) {
    document.getElementById('concluirMPMId').value = id;
    document.getElementById('concluirMPMMesText').textContent = mes_referencia || 'Visita';
    const modal = new bootstrap.Modal(document.getElementById('modalConcluirMPM'));
    modal.show();
};

document.addEventListener('DOMContentLoaded', () => {
    const formConcluirMPM = document.getElementById('formConcluirMPM');
    if (formConcluirMPM) {
        formConcluirMPM.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btnSubmit = document.getElementById('btnSubmitFormConcluirMPM');
            if (btnSubmit) { btnSubmit.disabled = true; btnSubmit.innerHTML = 'Salvando...'; }

            const formData = new FormData(formConcluirMPM);
            const id = formData.get('mpm_id');
            formData.set('status', 'CONCLUIDA');

            try {
                const res = await fetch('/elevadores/api/manutencao_preventiva/' + id + '/', {
                    method: 'PATCH',
                    headers: { 'X-CSRFToken': csrftoken },
                    body: formData
                });
                
                if (btnSubmit) { btnSubmit.disabled = false; btnSubmit.innerHTML = 'Confirmar Conclusão'; }

                if (res.ok) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalConcluirMPM'));
                    if (modal) modal.hide();
                    formConcluirMPM.reset();
                    loadMPMTable();
                    if (typeof Swal !== 'undefined') Swal.fire('Sucesso', 'MPM concluída com sucesso!', 'success');
                } else {
                    const errorData = await res.json();
                    console.error('Erro na API:', errorData);
                    if (typeof Swal !== 'undefined') Swal.fire('Erro', 'Erro ao concluir MPM. Verifique o console.', 'error'); else alert('Erro ao concluir MPM. Verifique o console.');
                }
            } catch (err) {
                console.error(err);
                if (btnSubmit) { btnSubmit.disabled = false; btnSubmit.innerHTML = 'Confirmar Conclusão'; }
            }
        });
    }
});

