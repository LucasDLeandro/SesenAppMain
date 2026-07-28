import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()
from django.apps import apps

res = []
keywords = ['nome', 'email', 'telefone', 'cpf', 'contato', 'sobrenome']
for m in apps.get_models():
    if m._meta.app_label in ['auth', 'admin', 'contenttypes', 'sessions', 'messages', 'authtoken', 'rest_framework']:
        continue
    fields = [f.name for f in m._meta.fields]
    matches = [f for f in fields if any(k in f.lower() for k in keywords)]
    if matches:
        res.append(f"{m._meta.app_label}.{m.__name__}: {matches}")

for r in res:
    print(r)
