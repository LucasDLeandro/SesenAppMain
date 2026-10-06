import sys

path = r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """<button class="btn btn-sm btn-outline-danger shadow-sm me-1" onclick="excluirSolicitacao(${data}, 'nada_consta', tabelaNadaConstaConcluido)" title="Excluir">"""

replacement = """<button class="btn btn-sm btn-outline-primary shadow-sm me-1" onclick="abrirModalDespachoSeiNadaConsta(${data})" title="Copiar Despacho SEI">
                                <i class="bi bi-clipboard-check"></i>
                            </button>
                            """ + target

if target in content:
    content = content.replace(target, replacement)
    
    append_str = """
async function abrirModalDespachoSeiNadaConsta(id) {
    try {
        const response = await fetch(`/telefonia/api/nada_consta/${id}/despacho_sei/`);
        if (!response.ok) throw new Error('Erro ao buscar texto');
        const data = await response.json();
        document.getElementById('texto_despacho_sei').value = data.texto || '';
        var modal = new bootstrap.Modal(document.getElementById('modal-despacho-sei-nada-consta'));
        modal.show();
    } catch(err) {
        console.error(err);
        if (typeof Swal !== 'undefined') {
            Swal.fire({icon: 'error', title: 'Erro', text: 'Falha ao carregar o despacho SEI.'});
        } else {
            alert('Falha ao carregar o despacho SEI.');
        }
    }
}
"""
    content += append_str
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Sucesso!")
else:
    print("Target not found!")
