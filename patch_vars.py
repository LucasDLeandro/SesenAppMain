import sys
p = r'C:\Lucas\SesenAppMain\notificacoes\templates\messages\includes\form_template_modal.html'
c = open(p,'r',encoding='utf-8').read()

target = """                        <div id="vars-tel-nada-consta" style="display:none;">
                            <small class="text-muted d-block mt-1 mb-1 fw-semibold" style="font-size: 0.72rem;">📝 Solicitação de Nada Consta:</small>
                            <ul class="mb-0 ps-3 text-muted" style="font-size: 0.75rem;">
                                <li><code>{tecnico}</code>: Nome do Contato</li>
                                <li><code>{nome}</code>: Nome do Solicitante (mesmo de Contato)</li>
                                <li><code>{protocolo}</code>: Número do SEI</li>
                            </ul>
                        </div>"""

replacement = """                        <div id="vars-tel-nada-consta" style="display:none;">
                            <small class="text-muted d-block mt-1 mb-1 fw-semibold" style="font-size: 0.72rem;">📝 Solicitação de Nada Consta:</small>
                            <ul class="mb-0 ps-3 text-muted" style="font-size: 0.75rem;">
                                <li><code>{tecnico}</code>: Nome do Contato</li>
                                <li><code>{nome}</code>: Nome do Solicitante (mesmo de Contato)</li>
                                <li><code>{protocolo}</code>: Número do SEI</li>
                            </ul>
                        </div>
                        <div id="vars-tel-nada-consta-conclusao" style="display:none;">
                            <small class="text-muted d-block mt-1 mb-1 fw-semibold" style="font-size: 0.72rem;">✅ Conclusão de Nada Consta:</small>
                            <ul class="mb-0 ps-3 text-muted" style="font-size: 0.75rem;">
                                <li><code>{protocolo}</code>: Número do SEI</li>
                                <li><code>{valor_devido}</code>: Valor Devido (Ex: 0,00 ou 15,30)</li>
                            </ul>
                        </div>"""

if 'vars-tel-nada-consta-conclusao' not in c:
    c = c.replace(target, replacement)
    open(p,'w',encoding='utf-8').write(c)
    print("Added vars-tel-nada-consta-conclusao!")
else:
    print("Already added.")
