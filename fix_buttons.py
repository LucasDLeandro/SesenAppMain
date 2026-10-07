import re

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<i class="fas fa-times"></i> Cancelar</button>', '<i class="fas fa-times"></i></button>')
content = content.replace('<i class="fas fa-times me-1"></i> Cancelar</button>', '<i class="fas fa-times"></i></button>')

# remove px-3 py-1 from the widget cancel buttons to make them smaller as well
content = content.replace('btn-outline-danger border-2 fw-bold px-3 py-1 text-nowrap', 'btn-outline-danger border-2 fw-bold px-2 py-1 text-nowrap')

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Buttons fixed!")
