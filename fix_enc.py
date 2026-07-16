# coding=utf-8
import re

with open('c:/Lucas/SesenAppMain/reembolsos/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'RELAT.*?RIO DE REEMBOLSO', 'RELATÓRIO DE REEMBOLSO', content)
content = re.sub(r'Emiss.*?:', 'Emissão:', content)
content = re.sub(r'Administra.*?o<br/>', 'Administração<br/>', content)
content = re.sub(r'Se.*?o de Equipamentos', 'Seção de Equipamentos', content)
content = re.sub(r'DADOS BANC.*?RIOS', 'DADOS BANCÁRIOS', content)
content = re.sub(r'Ag.*?ncia', 'Agência', content)
content = re.sub(r'M.*?VEL', 'MÓVEL', content)
content = re.sub(r'N.*? 11 DE 2022', 'Nº 11 DE 2022', content)
content = re.sub(r'Per.*?odo', 'Período', content)
content = re.sub(r'A Servi.*?o', 'A Serviço', content)
content = re.sub(r'Observa.*?es', 'Observações', content)
content = re.sub(r'apura.*?o', 'apuração', content)
content = re.sub(r'per.*?odo', 'período', content)
content = re.sub(r'm.*?vel', 'móvel', content)
content = re.sub(r'utilizar-se-.*?\s', 'utilizar-se-á ', content)
content = re.sub(r'Compet.*?ncia', 'Competência', content)
content = re.sub(r'm.*?s', 'mês', content)
content = re.sub(r'Instru.*?o', 'Instrução', content)
content = re.sub(r'n.*? 11/2022', 'nº 11/2022', content)
content = re.sub(r'est.*? a', 'está a', content)
content = re.sub(r'm.*?ximos', 'máximos', content)
content = re.sub(r'Designa.*?o', 'Designação', content)
content = re.sub(r'comiss.*?o', 'comissão', content)
content = re.sub(r'SOLICITA.*?O DE REEMBOLSO', 'SOLICITAÇÃO DE REEMBOLSO', content)

with open('c:/Lucas/SesenAppMain/reembolsos/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
