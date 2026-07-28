import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()
from django.test import RequestFactory
from usuarios.api_views import buscar_dados_pessoa_api
import traceback

req = RequestFactory().get('/?q=Lucas')
try:
    res = buscar_dados_pessoa_api(req)
    print("Status:", res.status_code)
    print("Content:", res.content.decode('utf-8'))
except Exception as e:
    traceback.print_exc()
