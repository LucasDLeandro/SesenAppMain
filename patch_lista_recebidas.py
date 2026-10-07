import re

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'r', encoding='utf-8') as f:
    content = f.read()

cancel_aparelho = """<button class="btn btn-sm btn-outline-danger text-nowrap" style="white-space: nowrap;" onclick="abrirModalCancelar(${row.id}, 'aparelhos')" title="Cancelar"><i class="fas fa-times"></i> Cancelar</button>"""
cancel_nada_consta = """<button class="btn btn-sm btn-outline-danger text-nowrap" style="white-space: nowrap;" onclick="abrirModalCancelar(${row.id}, 'nada_consta')" title="Cancelar"><i class="fas fa-times"></i> Cancelar</button>"""
cancel_senha = """<button class="btn btn-sm btn-outline-danger text-nowrap" style="white-space: nowrap;" onclick="abrirModalCancelar(${row.id}, 'senhas')" title="Cancelar"><i class="fas fa-times"></i> Cancelar</button>"""

# We also need to patch the widget (carregarListaRecebidasDashboard) around line 521:
cancel_widget_senha = """<button class="btn btn-sm btn-outline-danger border-2 fw-bold px-3 py-1 text-nowrap" style="border-radius: 6px;" onclick="fecharModalListaEExecutar('abrirModalCancelar', ${row.id}, 'senhas')"><i class="fas fa-times me-1"></i> Cancelar</button>"""
cancel_widget_nada_consta = """<button class="btn btn-sm btn-outline-danger border-2 fw-bold px-3 py-1 text-nowrap" style="border-radius: 6px;" onclick="fecharModalListaEExecutar('abrirModalCancelar', ${row.id}, 'nada_consta')"><i class="fas fa-times me-1"></i> Cancelar</button>"""
cancel_widget_aparelho = """<button class="btn btn-sm btn-outline-danger border-2 fw-bold px-3 py-1 text-nowrap" style="border-radius: 6px;" onclick="fecharModalListaEExecutar('abrirModalCancelar', ${row.id}, 'aparelhos')"><i class="fas fa-times me-1"></i> Cancelar</button>"""

def patch_modal(content):
    # Aparelhos Modal Recebidas
    # Search for `<button class="btn btn-sm btn-outline-success text-nowrap" style="white-space: nowrap;" onclick="abrirConclusao(${row.id})" title="Concluir Instalação">`
    # We add cancel right after it
    pattern_aparelho = r"(<button class=\"btn btn-sm btn-outline-success text-nowrap\" style=\"white-space: nowrap;\" onclick=\"abrirConclusao\(\$\{row\.id\}\)\" title=\"Concluir Instalação\">.*?<\/button>)"
    if cancel_aparelho not in content:
        content = re.sub(pattern_aparelho, r"\1\n                                        " + cancel_aparelho, content, flags=re.DOTALL)
        
    # Nada Consta Modal Recebidas
    pattern_nada = r"(<button class=\"btn btn-sm btn-outline-success text-nowrap\" style=\"white-space: nowrap;\" onclick=\\\"abrirModalConcluirNadaConsta\(\$\{row\.id\}[^\"]*?\" title=\"Concluir Nada Consta\">.*?<\/button>)"
    if cancel_nada_consta not in content:
        content = re.sub(pattern_nada, r"\1\n                                    " + cancel_nada_consta, content, flags=re.DOTALL)

    # Senhas Modal Recebidas
    pattern_senha = r"(<button class=\"btn btn-sm btn-outline-success text-nowrap\" style=\"white-space: nowrap;\" onclick=\"abrirModalConcluirSenha\(\$\{row\.id\}\)\" title=\"Concluir Geração de Senha\">.*?<\/button>)"
    if cancel_senha not in content:
        content = re.sub(pattern_senha, r"\1\n                                        " + cancel_senha, content, flags=re.DOTALL)
        
    return content

def patch_widget(content):
    # Widget Senha
    pattern_w_senha = r"(<button class=\"btn btn-sm btn-outline-success border-2 fw-bold px-3 py-1 text-nowrap\" style=\"border-radius: 6px;\" onclick=\"fecharModalListaEExecutar\('abrirModalConcluirSenha', \$\{row\.id\}\)\">.*?<\/button>)"
    if cancel_widget_senha not in content:
        content = re.sub(pattern_w_senha, r"\1\n                                " + cancel_widget_senha, content, flags=re.DOTALL)
        
    # Widget Nada Consta
    pattern_w_nada = r"(<button class=\"btn btn-sm btn-outline-success border-2 fw-bold px-3 py-1 text-nowrap\" style=\"border-radius: 6px;\" onclick=\"fecharModalListaEExecutar\('abrirModalConcluirNadaConsta', \$\{row\.id\}\)\">.*?<\/button>)"
    if cancel_widget_nada_consta not in content:
        content = re.sub(pattern_w_nada, r"\1\n                                " + cancel_widget_nada_consta, content, flags=re.DOTALL)
        
    # Widget Aparelho
    pattern_w_aparelho = r"(<button class=\"btn btn-sm btn-outline-success border-2 fw-bold px-3 py-1 text-nowrap\" style=\"border-radius: 6px;\" onclick=\"fecharModalListaEExecutar\('abrirConclusao', \$\{row\.id\}\)\">.*?<\/button>)"
    if cancel_widget_aparelho not in content:
        content = re.sub(pattern_w_aparelho, r"\1\n                                " + cancel_widget_aparelho, content, flags=re.DOTALL)
        
    return content

content = patch_modal(content)
content = patch_widget(content)

# We also need to fix `fecharModalListaEExecutar` to accept 3 arguments, because our new WIDGET cancels pass 3 arguments
# fecharModalListaEExecutar('abrirModalCancelar', ${row.id}, 'senhas')
# The original function probably looks like:
# function fecharModalListaEExecutar(funcName, id) { ... window[funcName](id); }
# We should change it to:
# function fecharModalListaEExecutar(funcName, ...args) { ... window[funcName](...args); }
pattern_func = r"function fecharModalListaEExecutar\(funcName, id\) \{"
if re.search(pattern_func, content):
    content = re.sub(pattern_func, "function fecharModalListaEExecutar(funcName, ...args) {", content)
    # also change window[funcName](id)
    content = re.sub(r"window\[funcName\]\(id\);", "window[funcName](...args);", content)

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("JS list_telefonia patched again!")
