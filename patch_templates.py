import sys

p = r'C:\Lucas\SesenAppMain\notificacoes\templates\messages\includes\form_template_modal.html'
c = open(p,'r',encoding='utf-8').read()

target = '<option value="tel_nada_consta" style="display: none;">Telefonia - Solicitação de Nada Consta</option>'
replacement = '<option value="tel_nada_consta" style="display: none;">Telefonia - Solicitação de Nada Consta</option>\n                        <option value="tel_nada_consta_conclusao" style="display: none;">Telefonia - Conclusão de Nada Consta (Despacho SEI)</option>'

if "tel_nada_consta_conclusao" not in c:
    c = c.replace(target, replacement)
    open(p,'w',encoding='utf-8').write(c)
    print("Fixed form_template_modal.html")

p = r'C:\Lucas\SesenAppMain\notificacoes\static\message_service\js\template_modal.js'
c = open(p,'r',encoding='utf-8').read()
if "tipo === 'tel_nada_consta_conclusao'" not in c:
    c = c.replace("tipo === 'tel_nada_consta'", "tipo === 'tel_nada_consta' || tipo === 'tel_nada_consta_conclusao'")
    open(p,'w',encoding='utf-8').write(c)
    print("Fixed template_modal.js")
