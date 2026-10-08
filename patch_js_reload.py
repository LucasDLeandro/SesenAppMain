import re

with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = "recarregarTabelas();"

new_code = """if ($.fn.DataTable.isDataTable('#tabela-recebidas-modal')) {
                $('#tabela-recebidas-modal').DataTable().ajax.reload(null, false);
            }
            if ($.fn.DataTable.isDataTable('#tabela-senhas')) {
                $('#tabela-senhas').DataTable().ajax.reload(null, false);
            }
            if ($.fn.DataTable.isDataTable('#tabela-nada-consta')) {
                $('#tabela-nada-consta').DataTable().ajax.reload(null, false);
            }"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(r'C:\Lucas\SesenAppMain\telefonia\static\telefonia\js\telefonia\list_telefonia.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("JS Reload Patch Applied!")
else:
    print("Could not find the target string in list_telefonia.js")
