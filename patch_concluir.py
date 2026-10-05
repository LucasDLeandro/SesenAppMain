import os
import re

js_list = r"C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js"
js_modal = r"C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\modal_forms.js"

# 1. Update list_telefonia.js
with open(js_list, 'r', encoding='utf-8') as f:
    content = f.read()

# Update the first call (buttons += `...`)
target1 = "onclick=\"abrirModalConcluirNadaConsta(${data}, '${row.protocolo}', '${new \nDate(row.data).toLocaleDateString('pt-BR')}', '${row.unidade}', '${row.servidor}', ${row.solicitar_desvinculacao ? \n'true' : 'false'}, '${ramal}')\""
replacement1 = "onclick=\"abrirModalConcluirNadaConsta(${data}, '${row.protocolo}', '${new Date(row.data).toLocaleDateString('pt-BR')}', '${row.unidade}', '${row.servidor}', ${row.solicitar_desvinculacao ? 'true' : 'false'}, '${ramal}', '${row.ramal || ''}', '${row.email || ''}')\""

# I will use a regex substitution to be safe
content = re.sub(r"onclick=\"abrirModalConcluirNadaConsta\(\$\{data\}, '\$\{row\.protocolo\}', '\$\{new Date\(row\.data\)\.toLocaleDateString\('pt-BR'\)\}', '\$\{row\.unidade\}', '\$\{row\.servidor\}', \$\{row\.solicitar_desvinculacao \? 'true' : 'false'\}, '\$\{ramal\}'\)\"",
                 r"onclick=\"abrirModalConcluirNadaConsta(${data}, '${row.protocolo}', '${new Date(row.data).toLocaleDateString(\'pt-BR\')}', '${row.unidade}', '${row.servidor}', ${row.solicitar_desvinculacao ? 'true' : 'false'}, '${ramal}', '${row.ramal || \'\'}', '${row.email || \'\'}')\"",
                 content)

# Update the second call
content = re.sub(r"onclick=\"abrirModalConcluirNadaConsta\(\$\{row\.id\}, '\$\{row\.protocolo\}', '\$\{new Date\(row\.data\)\.toLocaleDateString\('pt-BR'\)\}', '\$\{row\.unidade\}', '\$\{row\.servidor\}'\)\"",
                 r"onclick=\"abrirModalConcluirNadaConsta(${row.id}, '${row.protocolo}', '${new Date(row.data).toLocaleDateString(\'pt-BR\')}', '${row.unidade}', '${row.servidor}', false, '', '${row.ramal || \'\'}', '${row.email || \'\'}')\"",
                 content)

with open(js_list, 'w', encoding='utf-8') as f:
    f.write(content)


# 2. Update modal_forms.js
with open(js_modal, 'r', encoding='utf-8') as f:
    content2 = f.read()

target_func = r"function abrirModalConcluirNadaConsta(id, protocolo, dataStr, unidade, servidor, desvincular=false, ramalVinculado='') {"
replacement_func = r"function abrirModalConcluirNadaConsta(id, protocolo, dataStr, unidade, servidor, desvincular=false, ramalVinculado='', ramal='', email='') {"

target_body = r"document.getElementById('txt_servidor_nada_consta').innerText = servidor;"
replacement_body = r"document.getElementById('txt_servidor_nada_consta').innerText = servidor;" + "\n    if (document.getElementById('ramal_concluir_nada_consta')) document.getElementById('ramal_concluir_nada_consta').value = ramal;\n    if (document.getElementById('email_concluir_nada_consta')) document.getElementById('email_concluir_nada_consta').value = email;"

if target_func in content2:
    content2 = content2.replace(target_func, replacement_func)
if target_body in content2:
    content2 = content2.replace(target_body, replacement_body)

with open(js_modal, 'w', encoding='utf-8') as f:
    f.write(content2)

print("Updated both files successfully")
