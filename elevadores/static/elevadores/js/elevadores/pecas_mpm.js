
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || "";

async function loadMPMTable() {
    try {
        const response = await fetch("/elevadores/api/manutencao_preventiva/");
        if (!response.ok) throw new Error("Falha ao buscar MPM");
        const data = await response.json();
        
        const tbody = document.getElementById("mpm-tbody");
        if (!tbody) return;
        tbody.innerHTML = "";
        
        data.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${item.elevador}</td>
                <td>${item.mes_referencia}</td>
                <td>${item.data_execucao || "N/A"}</td>
                <td>${item.tecnico || "N/A"}</td>
                <td><span class="badge bg-${item.status === "EXECUTADO" ? "success" : "danger"}">${item.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteMPM(${item.id})"><i class="bi bi-trash"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Erro ao carregar MPM:", error);
    }
}

async function loadPecasTable() {
    try {
        const response = await fetch("/elevadores/api/peca_manutencao/");
        if (!response.ok) throw new Error("Falha ao buscar Peças");
        const data = await response.json();
        
        const tbody = document.getElementById("pecas-tbody");
        if (!tbody) return;
        tbody.innerHTML = "";
        
        data.forEach(item => {
            const isSub = item.status === "SUBSTITUIDA";
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${item.elevador}</td>
                <td>${item.andar}</td>
                <td>${item.tipo_peca}</td>
                <td>${item.ordem_servico || "-"}</td>
                <td>${item.tecnico_identificador || "-"}</td>
                <td>${item.data_registro}</td>
                <td>${item.data_previsao_troca}</td>
                <td>${item.tecnico || "-"}</td>
                <td>${item.data_efetiva_troca || "-"}</td>
                <td><span class="badge bg-${isSub ? "success" : "warning text-dark"}">${item.status}</span></td>
                <td>
                    ${!isSub ? `<button class="btn btn-sm btn-success me-1" onclick="openConcluirModal(${item.id})"><i class="bi bi-check-lg"></i> Concluir</button>` : ""}
                    <button class="btn btn-sm btn-outline-danger" onclick="deletePeca(${item.id})"><i class="bi bi-trash"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Erro ao carregar Peças:", error);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadMPMTable();
    loadPecasTable();

    // Submit Cadastro MPM
    const formMPM = document.getElementById("formCadastroMPM");
    if (formMPM) {
        formMPM.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const payload = {
                elevador: document.getElementById("mpmElevador").value,
                mes_referencia: document.getElementById("mpmMes").value + "-01",
                status: document.getElementById("mpmStatus").value,
                data_execucao: document.getElementById("mpmDataExecucao").value || null,
                ordem_servico: document.getElementById("mpmOS").value,
                tecnico: document.getElementById("mpmTecnico").value
            };

            try {
                const res = await fetch("/elevadores/api/manutencao_preventiva/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById("modalCadastroMPM"));
                    modal.hide();
                    formMPM.reset();
                    loadMPMTable();
                } else {
                    alert("Erro ao salvar MPM");
                }
            } catch (err) { console.error(err); }
        });
    }

    // Submit Cadastro Peça
    const formPeca = document.getElementById("formCadastroPeca");
    if (formPeca) {
        formPeca.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const payload = {
                elevador: document.getElementById("pecaElevador").value,
                andar: document.getElementById("pecaAndar").value,
                tipo_peca: document.getElementById("pecaTipo").value,
                data_previsao_troca: document.getElementById("pecaPrevisao").value,
                ordem_servico: document.getElementById("pecaOS") ? document.getElementById("pecaOS").value : "",
                tecnico_identificador: document.getElementById("pecaTecnicoIdentificador") ? document.getElementById("pecaTecnicoIdentificador").value : "",
                status: "PENDENTE"
            };

            try {
                const res = await fetch("/elevadores/api/peca_manutencao/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
                    body: JSON.stringify(payload)
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

window.deleteMPM = async function(id) {
    if(!confirm("Deseja realmente apagar este registro MPM?")) return;
    try {
        const res = await fetch(`/elevadores/api/manutencao_preventiva/${id}/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": csrftoken }
        });
        if (res.ok) loadMPMTable();
    } catch(e) { console.error(e); }
}

window.deletePeca = async function(id) {
    if(!confirm("Deseja realmente apagar esta peça?")) return;
    try {
        const res = await fetch(`/elevadores/api/peca_manutencao/${id}/`, {
            method: "DELETE",
            headers: { "X-CSRFToken": csrftoken }
        });
        if (res.ok) loadPecasTable();
    } catch(e) { console.error(e); }
}

