import re

with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Restore the cancelar methods to original state
old_cancelar = """    @action(detail=True, methods=['post'], authentication_classes=[], permission_classes=[])"""
new_cancelar = """    @action(detail=True, methods=['post'])"""

content = content.replace(old_cancelar, new_cancelar)

with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Auth Restored!")
