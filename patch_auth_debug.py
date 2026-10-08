import re

with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the cancelar method in CriarSenhaViewSet to have authentication_classes=[] and permission_classes=[]
old_cancelar = """    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):"""

new_cancelar = """    @action(detail=True, methods=['post'], authentication_classes=[], permission_classes=[])
    def cancelar(self, request, pk=None):"""

content = content.replace(old_cancelar, new_cancelar)

with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Auth Debug Patch Applied!")
