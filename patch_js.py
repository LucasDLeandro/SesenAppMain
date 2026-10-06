import sys
p = r'C:\Lucas\SesenAppMain\notificacoes\static\message_service\js\template_modal.js'
c = open(p,'r',encoding='utf-8').read()

# Variables declarations
target1 = "var varsTelNadaConsta   = document.getElementById('vars-tel-nada-consta');"
repl1 = "var varsTelNadaConsta   = document.getElementById('vars-tel-nada-consta');\n        var varsTelNadaConstaConclusao = document.getElementById('vars-tel-nada-consta-conclusao');"
c = c.replace(target1, repl1)

# Hiding logic
target2 = "if (varsTelNadaConsta)   varsTelNadaConsta.style.display   = 'none';"
repl2 = "if (varsTelNadaConsta)   varsTelNadaConsta.style.display   = 'none';\n        if (varsTelNadaConstaConclusao) varsTelNadaConstaConclusao.style.display = 'none';"
c = c.replace(target2, repl2)

# Showing logic
target3 = """            if (tipoEvento === 'tel_nada_consta') {
                if (varsTelNadaConsta) varsTelNadaConsta.style.display = 'block';
            }"""
repl3 = """            if (tipoEvento === 'tel_nada_consta') {
                if (varsTelNadaConsta) varsTelNadaConsta.style.display = 'block';
            }
            if (tipoEvento === 'tel_nada_consta_conclusao') {
                if (varsTelNadaConstaConclusao) varsTelNadaConstaConclusao.style.display = 'block';
            }"""
c = c.replace(target3, repl3)

open(p,'w',encoding='utf-8').write(c)
print("Patched JS!")
