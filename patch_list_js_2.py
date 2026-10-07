import re

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'r', encoding='utf-8') as f:
    content = f.read()

def inject_cancel_button(content, table_init_func, entity_type):
    # Find the function
    match = re.search(r"function " + table_init_func + r"\(\).*?\{", content, re.DOTALL)
    if not match: return content
    start = match.end()
    # Find the render function inside columnDefs for the actions column
    # Typically it ends with the last column. Let's find "return `" or "return '" inside the render block
    # Actually, we can just replace the closing tag of the visualizer/editor button block.
    # We will look for:
    # `${row.status === 'em_aberto' ? `<button class="btn btn-sm btn-success"...>...` : ''}`
    # and add the cancelar button right after it.
    
    # Let's find the `render:` function block inside the table definition
    end_of_func = content.find("});", start)
    if end_of_func == -1: end_of_func = content.find("}\n", start)
    
    block = content[start:end_of_func]
    
    # Find the pattern where we output the actions HTML
    # Ex:
    # ${row.status === 'em_aberto' ? `<button class="btn btn-sm btn-success"...><i class="fas fa-check"></i></button>` : ''}
    # It might vary. Let's just append it before `</div>` or `</td>` or just before the end of the return string.
    # Actually, the template uses literal template strings returning HTML.
    
    # We can inject our Cancelar button in the action column.
    cancel_button_html = f"\n                        ${{row.status === 'em_aberto' ? `<button class=\"btn btn-sm btn-danger\" title=\"Cancelar\" onclick=\"abrirModalCancelar(${'{row.id}'}, '{entity_type}')\"><i class=\"fas fa-times\"></i></button>` : ''}}"
    
    # Look for the last button before the backtick closes
    # Easiest way: look for `</button>` : ''}` or similar pattern and inject after it.
    
    # For Aparelhos:
    if entity_type == 'aparelhos':
        block_new = re.sub(
            r"(\$\{row\.status === 'em_aberto' \? `<button class=\"btn btn-sm btn-success\".*?><i class=\"fas fa-check\"></i></button>` : ''\})",
            r"\1" + cancel_button_html.replace('"', '\\"'),
            block
        )
    elif entity_type == 'senhas':
        block_new = re.sub(
            r"(\$\{row\.status === 'em_aberto' \? `<button class=\"btn btn-sm btn-success\" onclick=\"abrirModalConcluirSenha\(\$\{row\.id\}\)\"><i class=\"fas fa-check\"></i></button>` : ''\})",
            r"\1" + cancel_button_html.replace('"', '\\"'),
            block
        )
    elif entity_type == 'nada_consta':
        block_new = re.sub(
            r"(\$\{row\.status === 'em_aberto' \? `<button class=\"btn btn-sm btn-success me-1\" onclick=\"abrirModalConcluirNadaConsta\(\$\{row\.id\}\)\"><i class=\"fas fa-check\"></i></button>` : ''\})",
            r"\1" + cancel_button_html.replace('"', '\\"'),
            block
        )
    else:
        block_new = block

    # Let's use a simpler regex if the above doesn't match
    if block == block_new:
        # Fallback: find the last </button>` and insert there
        # Wait, the string might have `<button...><i class="fas fa-check"></i></button>\` : ''}`
        # Let's just insert it right before the last closing backtick of the return statement
        block_new = re.sub(
            r"(\$\{row\.status === 'em_aberto'.*?\})",
            r"\1" + cancel_button_html.replace('"', '\\"'),
            block
        )
        
    return content[:start] + block_new + content[end_of_func:]

content = inject_cancel_button(content, "initTabelaSolicitacoesAparelhos", "aparelhos")
content = inject_cancel_button(content, "initTabelaSolicitacoesSenhas", "senhas")
content = inject_cancel_button(content, "initTabelaNadaConsta", "nada_consta")

# Add the JS functions for cancellation at the end of the file
js_logic = """
// Lógica de Cancelamento Global
function abrirModalCancelar(id, tipo) {
    $('#cancelar-id').val(id);
    $('#cancelar-tipo').val(tipo);
    $('#form-cancelar')[0].reset();
    $('#modal-cancelar').modal('show');
}

$('#form-cancelar').on('submit', function(e) {
    e.preventDefault();
    let id = $('#cancelar-id').val();
    let tipo = $('#cancelar-tipo').val();
    let justificativa = $('#justificativa_cancelamento').val().trim();
    
    if(!justificativa) {
        Swal.fire('Atenção', 'Justificativa é obrigatória.', 'warning');
        return;
    }
    
    let endpoint = '';
    if(tipo === 'aparelhos') {
        endpoint = `/telefonia/api/aparelhos/${id}/cancelar/`;
    } else if (tipo === 'senhas') {
        endpoint = `/telefonia/api/senhas/${id}/cancelar/`;
    } else if (tipo === 'nada_consta') {
        endpoint = `/telefonia/api/nada_consta/${id}/cancelar/`;
    }
    
    $.ajax({
        url: endpoint,
        method: 'POST',
        data: JSON.stringify({ justificativa: justificativa }),
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function() {
            $('#modal-cancelar').modal('hide');
            Swal.fire('Sucesso', 'Solicitação cancelada com sucesso.', 'success');
            recarregarTabelas();
        },
        error: function(err) {
            Swal.fire('Erro', 'Ocorreu um erro ao cancelar.', 'error');
        }
    });
});
"""

if "function abrirModalCancelar(" not in content:
    content += "\n" + js_logic

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("JS list_telefonia patched!")
