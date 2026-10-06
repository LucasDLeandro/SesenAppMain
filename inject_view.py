import sys

path = r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Pendente Nada Consta
target_pendente = """<button class="btn btn-sm btn-outline-success text-nowrap" style="white-space: nowrap;" onclick=\\"abrirModalConcluirNadaConsta(${row.id}"""
replacement_pendente = """<button class="btn btn-sm btn-outline-info text-nowrap me-1" onclick="abrirModalVisualizarNadaConsta(${row.id})" title="Visualizar Nada Consta"><i class="bi bi-eye-fill"></i></button>
                                    <button class="btn btn-sm btn-outline-success text-nowrap" style="white-space: nowrap;" onclick=\\"abrirModalConcluirNadaConsta(${row.id}"""

content = content.replace(target_pendente, replacement_pendente)

# Replace Concluida Nada Consta
target_concluida = """<button class="btn btn-sm btn-outline-primary shadow-sm me-1" onclick="abrirModalDespachoSeiNadaConsta(${data})" title="Copiar Despacho SEI">"""
replacement_concluida = """<button class="btn btn-sm btn-outline-info shadow-sm me-1" onclick="abrirModalVisualizarNadaConsta(${data})" title="Visualizar">
                                <i class="bi bi-eye-fill"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-primary shadow-sm me-1" onclick="abrirModalDespachoSeiNadaConsta(${data})" title="Copiar Despacho SEI">"""

content = content.replace(target_concluida, replacement_concluida)

# Append function
append_str = """
function abrirModalVisualizarNadaConsta(id) {
    fetch(`/telefonia/api/nada_consta/${id}/`)
    .then(response => response.json())
    .then(data => {
        document.getElementById('vis-nada-consta-protocolo').innerText = data.protocolo || '-';
        document.getElementById('vis-nada-consta-data').innerText = data.data ? new Date(data.data).toLocaleDateString('pt-BR') : '-';
        document.getElementById('vis-nada-consta-servidor').innerText = data.servidor || '-';
        document.getElementById('vis-nada-consta-unidade').innerText = data.unidade || '-';
        document.getElementById('vis-nada-consta-email').innerText = data.email_cadastrado || '-';
        document.getElementById('vis-nada-consta-ramal').innerText = data.ramal || '-';
        document.getElementById('vis-nada-consta-valor').innerText = data.valor_devido ? 'R$ ' + data.valor_devido.replace('.', ',') : 'R$ 0,00';
        document.getElementById('vis-nada-consta-tecnico').innerText = data.tecnico_responsavel || '-';
        document.getElementById('vis-nada-consta-desvinculacao').checked = data.solicitar_desvinculacao || false;
        
        var modal = new bootstrap.Modal(document.getElementById('modal-visualizar-nada-consta'));
        modal.show();
    })
    .catch(error => {
        console.error('Erro:', error);
        if (typeof Swal !== 'undefined') {
            Swal.fire({icon: 'error', title: 'Erro', text: 'Não foi possível carregar os dados.'});
        } else {
            alert('Não foi possível carregar os dados.');
        }
    });
}
"""

if "function abrirModalVisualizarNadaConsta" not in content:
    content += append_str

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Injection success")
