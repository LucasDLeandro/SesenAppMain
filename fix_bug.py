import os

js_file = r"C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js"
with open(js_file, 'r', encoding='utf-8') as f:
    js_content = f.read()

target = r"onclick=\"" + r"abrirModalConcluirNadaConsta(${row.id}, '${row.protocolo}', '${new Date(row.data).toLocaleDateString(\'pt-BR\')}', '${row.unidade}', '${row.servidor}', false, '', '${row.ramal || \'\'}', '${row.email || \'\'}')" + r"\""

replacement = r"onclick=\"abrirModalConcluirNadaConsta(${row.id}, '${row.protocolo}', '${new Date(row.data).toLocaleDateString('pt-BR')}', '${row.unidade}', '${row.servidor}', false, '', '${row.ramal || ''}', '${row.email || ''}')\""

js_content = js_content.replace(target, replacement)

with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Updated list_telefonia.js again")
