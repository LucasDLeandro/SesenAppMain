import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

c = Client()
user = User.objects.first()
c.force_login(user)

try:
    response = c.get('/contratos/api/pagamentos/', SERVER_NAME='localhost', HTTP_ACCEPT='application/json')
    print('STATUS:', response.status_code)
    print('URL:', getattr(response, 'redirect_chain', 'No redirect'))
    print('CONTENT:', response.content.decode('utf-8')[:1000])
except Exception as e:
    import traceback
    traceback.print_exc()
