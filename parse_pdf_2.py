import re

with open("parse_pdf.py", "r", encoding="utf-8") as f:
    content = f.read()
    
# Extract the text block
text_start = content.find('text = """') + 10
text_end = content.find('"""', text_start)
text = content[text_start:text_end]

matches = []
lines = text.split("\n")
for i, line in enumerate(lines):
    match_patrimonio = re.search(r"^\d+\s+([R\d]+)\s+APARELHO", line)
    if match_patrimonio:
        patrimonio = match_patrimonio.group(1)
        modelo_match = re.search(r"MODELO:\s*(\d+)", line)
        modelo = modelo_match.group(1) if modelo_match else "4038"
        if i + 1 < len(lines):
            next_line = lines[i+1]
            serie_match = re.search(r"SERIE:\s*([A-Z0-9]+)", next_line)
            if serie_match:
                serie = serie_match.group(1)
                matches.append(f"    AparelhoVoip(patrimonio='{patrimonio}', modelo='{modelo}', fcn='{serie}'),")

with open("out.py", "w", encoding="utf-8") as f:
    f.write("lista_aparelhos = [\n")
    f.write("\n".join(matches) + "\n")
    f.write("]\n")
