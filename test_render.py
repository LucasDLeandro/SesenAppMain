import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SesenAppMain.settings")
django.setup()

from django.test import RequestFactory
from adm_setup.views.conf_whats_notif_view import gerenciar_notificacao

request = RequestFactory().get('/adm_setup/notificacao_elev/')
response = gerenciar_notificacao(request)
html = response.content.decode('utf-8')

print('ID_TEMPLATE_EXISTS:', 'name="id_template"' in html)
print('BASE_TEXT_EXISTS:', 'name="base_text"' in html)
print('TIPO_EVENTO_EXISTS:', 'name="tipo_evento"' in html)

idx = html.find('id_id_template')
if idx != -1:
    print("Found id_id_template. Context around it:")
    print(html[max(0, idx-500):min(len(html), idx+500)])
else:
    print("Did NOT find id_id_template!")
