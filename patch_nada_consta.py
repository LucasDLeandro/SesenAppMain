import re

with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the block
old_block = """            # Disparar notificação de conclusão para o servidor
            template = TemplateMessage.objects.filter(tipo_evento='tel_nada_consta_conclusao', is_ativo=True).first()
            if template and solicitacao.email_cadastrado:
                from notificacoes.services import disparar_notificacao_avulso
                texto = template.base_text
                try:
                    valor_str = str(solicitacao.valor_devido) if solicitacao.valor_devido else '0.00'
                    text = texto.format(
                        protocolo=solicitacao.protocolo or 'N/A',
                        unidade=solicitacao.unidade or 'N/A',
                        sigla_unidade=solicitacao.sigla_unidade or 'N/A',
                        servidor=solicitacao.servidor or 'N/A',
                        ramal=solicitacao.ramal or 'N/A',
                        email_cadastrado=solicitacao.email_cadastrado or 'N/A',
                        valor_devido=str(valor_str).replace('.', ','),
                        tecnico=solicitacao.tecnico_responsavel or 'N/A',
                        data=solicitacao.data.strftime('%d/%m/%Y') if solicitacao.data else 'N/A'
                    )
                    assunto = f"Conclusão de Nada Consta - {solicitacao.protocolo or 'N/A'}"
                    disparar_notificacao_avulso(solicitacao.email_cadastrado, text, text, assunto)
                except Exception as e:
                    print(f"Erro ao formatar/enviar mensagem de conclusão (Nada Consta): {e}")"""

new_block = """            # Disparar notificação de conclusão para a equipe
            template = TemplateMessage.objects.filter(tipo_evento='tel_nada_consta_conclusao', is_ativo=True).first()
            if template:
                from notificacoes.models.contato_notificacao import Contato
                from notificacoes.services import disparar_notificacao_contato
                
                contatos = Contato.objects.filter(is_ativo=True, notifica_telefonia=True)
                enviados = set()
                for contato in contatos:
                    chave_duplicidade = getattr(contato, '_telefone_sanitizado', contato.telefone) or (contato.pessoa.email if contato.pessoa else None)
                    if chave_duplicidade:
                        if chave_duplicidade in enviados:
                            continue
                        enviados.add(chave_duplicidade)
                    
                    texto = template.base_text
                    try:
                        valor_str = str(solicitacao.valor_devido) if solicitacao.valor_devido else '0.00'
                        text = texto.format(
                            protocolo=solicitacao.protocolo or 'N/A',
                            unidade=solicitacao.unidade or 'N/A',
                            sigla_unidade=solicitacao.sigla_unidade or 'N/A',
                            servidor=solicitacao.servidor or 'N/A',
                            ramal=solicitacao.ramal or 'N/A',
                            email_cadastrado=solicitacao.email_cadastrado or 'N/A',
                            valor_devido=str(valor_str).replace('.', ','),
                            tecnico=solicitacao.tecnico_responsavel or 'N/A',
                            data=solicitacao.data.strftime('%d/%m/%Y') if solicitacao.data else 'N/A'
                        )
                        assunto = f"Conclusão de Nada Consta - {solicitacao.protocolo or 'N/A'}"
                        disparar_notificacao_contato(contato, text, text, assunto)
                    except Exception as e:
                        print(f"Erro ao formatar/enviar mensagem de conclusão (Nada Consta) para equipe: {e}")"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched successfully!")
else:
    print("Old block not found!")
