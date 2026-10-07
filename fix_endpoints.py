import re

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix aparelhos
content = content.replace("endpoint = `/telefonia/api/aparelhos/${id}/cancelar/`;", "endpoint = `/telefonia/api/solicitacoes/${id}/cancelar/`;")

# Fix senhas
content = content.replace("endpoint = `/telefonia/api/senhas/${id}/cancelar/`;", "endpoint = `/telefonia/api/solicitacoes-senhas/${id}/cancelar/`;")

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Endpoints fixed!")
