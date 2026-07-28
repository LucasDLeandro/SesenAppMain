import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()
from django.apps import apps

models_to_check = [
    'notificacoes.Contato',
    'reembolsos.ServidorReembolso',
    'equipe_tecnica.Tecnico',
    'usuarios.Pessoa',
    'usuarios.Perfil',
]

for model_path in models_to_check:
    app_label, model_name = model_path.split('.')
    m = apps.get_model(app_label, model_name)
    print(f"\n--- {m.__name__} ---")
    for f in m._meta.fields:
        print(f"{f.name}: {f.get_internal_type()}")
