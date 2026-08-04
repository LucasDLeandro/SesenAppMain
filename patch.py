import os
import re

files = [
    r'C:\Lucas\SesenAppMain\contratos\templates\contratos\dashboard_contratos.html',
    r'C:\Lucas\SesenAppMain\contratos\templates\contratos\pagamentos.html',
    r'C:\Lucas\SesenAppMain\contratos\templates\contratos\visao_geral_contrato.html'
]

html_old = '''<h6 style="color: #3b82f6;">Vinculação de Pagamento</h6>
                              <div class="row g-3 mt-1">
                                  <div class="col-md-8">
                                      <label class="form-label">Ordem de Pagamento (Doc. SEI, SIAFI, etc)</label>
                                      <input type="text" class="form-control" id="input_ordem_pagamento" placeholder="Ex: OB 2026OB123456">
                                  </div>
                                  <div class="col-md-4">
                                      <label class="form-label">Status</label>
                                      <select class="form-select" id="input_status">
                                          <option value="PENDENTE">PENDENTE</option>
                                          <option value="PAGO">PAGO</option>
                                      </select>
                                  </div>
                              </div>'''

html_new = '''<h6 style="color: #3b82f6;">Vinculação de Pagamento</h6>
                              <div class="row g-3 mt-1">
                                  <div class="col-md-6">
                                      <label class="form-label">Ordem de Pagamento (Doc. SEI, SIAFI, etc)</label>
                                      <input type="text" class="form-control" id="input_ordem_pagamento" placeholder="Ex: OB 2026OB123456">
                                  </div>
                                  <div class="col-md-6">
                                      <label class="form-label">Nota Técnica de Liquidação de Despesas</label>
                                      <input type="text" class="form-control" id="input_nota_liquidacao" placeholder="Ex: SEI 1234567">
                                  </div>
                                  <div class="col-md-6">
                                      <label class="form-label">Valor Pago (R$)</label>
                                      <input type="text" class="form-control" id="input_valor_pago" placeholder="0,00">
                                  </div>
                                  <div class="col-md-6">
                                      <label class="form-label">Status</label>
                                      <select class="form-select" id="input_status">
                                          <option value="PENDENTE">PENDENTE</option>
                                          <option value="PAGO">PAGO</option>
                                      </select>
                                  </div>
                              </div>'''

js_abrir_old = '''        document.getElementById('input_ordem_pagamento').value = pag.ordem_pagamento || '';
        document.getElementById('input_status').value = pag.status;'''

js_abrir_new = '''        document.getElementById('input_ordem_pagamento').value = pag.ordem_pagamento || '';
        document.getElementById('input_nota_liquidacao').value = pag.protocolo_nota_liquidacao || '';
        document.getElementById('input_valor_pago').value = pag.valor_pago ? formatCurrency(pag.valor_pago).replace('R$', '').trim() : '';
        document.getElementById('input_status').value = pag.status;'''

js_salvar_old = '''        const ordem = document.getElementById('input_ordem_pagamento').value;
        const status = document.getElementById('input_status').value;

        const csrftoken = getCookie('csrftoken');'''

js_salvar_new = '''        const ordem = document.getElementById('input_ordem_pagamento').value;
        const notaLiq = document.getElementById('input_nota_liquidacao').value;
        const valorStr = document.getElementById('input_valor_pago').value;
        const status = document.getElementById('input_status').value;

        let valorPagoFormatado = valorStr.replace(/\./g, '').replace(',', '.');
        if(!valorPagoFormatado || isNaN(valorPagoFormatado)) valorPagoFormatado = 0;

        const csrftoken = getCookie('csrftoken');'''

js_body_old = '''            body: JSON.stringify({
                ordem_pagamento: ordem,
                status: status
            })'''

js_body_new = '''            body: JSON.stringify({
                ordem_pagamento: ordem,
                protocolo_nota_liquidacao: notaLiq,
                valor_pago: valorPagoFormatado,
                status: status
            })'''

# Allow varied indentation by using regex
def replace_whitespace(text):
    return re.sub(r'[ \t]+', r'[ \t]+', re.escape(text)).replace(r'\n', r'\s*\n\s*')

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacing HTML
    pattern_html = replace_whitespace(html_old)
    content = re.sub(pattern_html, html_new, content)

    # Replacing JS Abrir
    pattern_abrir = replace_whitespace(js_abrir_old)
    content = re.sub(pattern_abrir, js_abrir_new, content)

    # Replacing JS Salvar
    pattern_salvar = replace_whitespace(js_salvar_old)
    content = re.sub(pattern_salvar, js_salvar_new, content)

    # Replacing JS Body
    pattern_body = replace_whitespace(js_body_old)
    content = re.sub(pattern_body, js_body_new, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {file_path}")
