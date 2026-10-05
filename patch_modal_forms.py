import os

js_file = r"C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\modal_forms.js"
with open(js_file, 'r', encoding='utf-8') as f:
    content = f.read()

target1 = '''                                inputServidor.value = item.nome;
                                hiddenCpf.value = item.cpf || '';
                                hiddenMatricula.value = item.matricula || '';'''

replacement1 = '''                                inputServidor.value = item.nome;
                                hiddenCpf.value = item.cpf || '';
                                hiddenMatricula.value = item.matricula || '';
                                if (document.getElementById('ramal_nada_consta')) document.getElementById('ramal_nada_consta').value = item.ramal || '';
                                if (document.getElementById('email_nada_consta')) document.getElementById('email_nada_consta').value = item.email || '';'''

target2 = '''                servidor: document.getElementById('servidor_nada_consta').value,
                cpf: document.getElementById('hidden_cpf_nada_consta').value,
                matricula: document.getElementById('hidden_matricula_nada_consta').value,'''

replacement2 = '''                servidor: document.getElementById('servidor_nada_consta').value,
                cpf: document.getElementById('hidden_cpf_nada_consta').value,
                matricula: document.getElementById('hidden_matricula_nada_consta').value,
                ramal: document.getElementById('ramal_nada_consta') ? document.getElementById('ramal_nada_consta').value : '',
                email: document.getElementById('email_nada_consta') ? document.getElementById('email_nada_consta').value : '','''

if target1 in content:
    content = content.replace(target1, replacement1)
if target2 in content:
    content = content.replace(target2, replacement2)

with open(js_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("modal_forms.js patched")
