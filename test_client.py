import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sesen_app.settings")
django.setup()
from django.test import Client
from usuarios.models import Perfil

user = Perfil.objects.get(user__username='lucas.leandro.adml').user
client = Client()
client.force_login(user)

response = client.get('/elevadores/api/elevadoress/dashboard/?inicio=2026-07-01&fim=2026-07-31', HTTP_HOST='127.0.0.1')
print(f"Status: {response.status_code}")
if response.status_code == 302:
    print(f"Redirecting to: {response.url}")
elif response.status_code == 500:
    html = response.content.decode('utf-8')
    if 'Exception Value:' in html:
        start = html.find('Exception Value:')
        end = html.find('</pre>', start)
        print(html[start:end])
    else:
        print(html[:2000])
else:
    print("Success")
