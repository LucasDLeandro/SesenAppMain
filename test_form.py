import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SesenAppMain.settings")
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from adm_setup.views.conf_whats_notif_view import gerenciar_notificacao

req = RequestFactory().get('/adm_setup/notificacao_elev/')
req.user = AnonymousUser()

try:
    r = gerenciar_notificacao(req)
    form = r.context_data['criarTemplate']
    print('Form class:', form.__class__.__name__)
    print('Fields in form:')
    for name, field in form.fields.items():
        print(f" - {name}: {field.__class__.__name__}")
        print(f"   Widget: {field.widget.__class__.__name__}")
        print(f"   Rendered: {field.widget.render(name, None)}")
        
    print("\n--- Testing Rendered Template ---")
    html = r.content.decode('utf-8')
    import re
    print("Found base_text inputs:", re.findall(r'<[^>]*name=\"base_text\"[^>]*>', html))
    print("Found id_template inputs:", re.findall(r'<[^>]*name=\"id_template\"[^>]*>', html))
except Exception as e:
    import traceback
    traceback.print_exc()
