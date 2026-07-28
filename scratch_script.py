import re

path_pagamentos = r"c:\Lucas\SesenAppMain\contratos\templates\contratos\pagamentos.html"
path_dashboard = r"c:\Lucas\SesenAppMain\contratos\templates\contratos\dashboard_contratos.html"

with open(path_pagamentos, "r", encoding="utf-8") as f:
    content_pagamentos = f.read()

# Extract modal
modal_match = re.search(r'(<!-- Modal Detalhes do Pagamento -->.*?</div>\s*</div>\s*</div>)', content_pagamentos, re.DOTALL)
modal_html = modal_match.group(1) if modal_match else ""

# Extract extra_js
js_match = re.search(r'({% block extra_js %}.*?{% endblock %})', content_pagamentos, re.DOTALL)
js_html = js_match.group(1) if js_match else ""

# Replace 'modalPagamento' with 'modalDetalhesPagamento' to avoid conflicts
modal_html = modal_html.replace('id="modalPagamento"', 'id="modalDetalhesPagamento"')
js_html = js_html.replace("getElementById('modalPagamento')", "getElementById('modalDetalhesPagamento')")
# Rename function abrirModal to abrirModalDetalhesPagamento just in case
js_html = js_html.replace('window.abrirModal = function(id)', 'window.abrirModalDetalhesPagamento = function(id)')
js_html = js_html.replace('onclick="abrirModal(${pag.id})"', 'onclick="abrirModalDetalhesPagamento(${pag.id})"')

with open(path_dashboard, "r", encoding="utf-8") as f:
    content_dashboard = f.read()

# The file dashboard_contratos.html ends with {% endblock %}
# We replace the last {% endblock %} with our new content.
if "{% endblock %}" in content_dashboard:
    content_dashboard = content_dashboard.rsplit("{% endblock %}", 1)
    new_content = f"{content_dashboard[0]}\n\n{modal_html}\n\n{{% endblock %}}\n\n{js_html}\n"
    
    with open(path_dashboard, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Dashboard modificado com sucesso.")
else:
    print("Erro: não achou {% endblock %}")
