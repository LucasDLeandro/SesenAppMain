import sys

p = r'C:\Lucas\SesenAppMain\notificacoes\templates\messages\includes\form_template_modal.html'
c = open(p,'r',encoding='utf-8').read()

target2 = '<option value="tel_nada_consta">Telefonia - Solicitação de Nada Consta</option>'
replacement2 = '<option value="tel_nada_consta">Telefonia - Solicitação de Nada Consta</option>\n                        <option value="tel_nada_consta_conclusao">Telefonia - Conclusão de Nada Consta (Despacho SEI)</option>'

if target2 in c:
    c = c.replace(target2, replacement2)
    open(p,'w',encoding='utf-8').write(c)
    print("Fixed form_template_modal.html")
else:
    print("Target 2 not found!")
