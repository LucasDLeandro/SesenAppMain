import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User
import re
user = User.objects.first()
c = Client(SERVER_NAME='127.0.0.1')
c.force_login(user)
res = c.get('/elevadores/api/eleva_os/?fim=2026-08-31', follow=True)
print('Status:', res.status_code)
if res.status_code == 500:
    html = res.content.decode('utf-8')
    m = re.search(r'<div class="exception_value">(.*?)</div>', html, re.DOTALL)
    if m: print('EXCEPTION:', m.group(1).strip())
