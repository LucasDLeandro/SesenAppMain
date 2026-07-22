import os

agents_dir = r"C:\Lucas\SesenAppMain\.agents"
if not os.path.exists(agents_dir):
    os.makedirs(agents_dir)

agents_file = os.path.join(agents_dir, "AGENTS.md")
rule_text = "\n- Sempre salve as alterações no git após a execução de tarefas (ex: git add . && git commit -m \"Auto commit by Agent\"), para não perder histórico de modificações.\n"

if os.path.exists(agents_file):
    with open(agents_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if "- Sempre salve as alterações no git após a execução de tarefas" not in content:
        content += rule_text
        with open(agents_file, 'w', encoding='utf-8') as f:
            f.write(content)
else:
    with open(agents_file, 'w', encoding='utf-8') as f:
        f.write("# Regras do Projeto SesenAppMain\n" + rule_text)

print("Rule added to AGENTS.md")
