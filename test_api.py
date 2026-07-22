import os
import django
from django.test import RequestFactory
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()

from elevadores.views.elev_drf_viewset import ElevadorViewSet
from django.contrib.auth import get_user_model

factory = RequestFactory()
User = get_user_model()
user = User.objects.filter(is_superuser=True).first()

view = ElevadorViewSet.as_view({'get': 'dashboard'})

urls = [
    '/elevadores/api/elevadoress/dashboard/',
    '/elevadores/api/elevadoress/dashboard/?inicio=2026-07-01&fim=2026-07-31',
    '/elevadores/api/elevadoress/dashboard/?inicio=2026-06-01&fim=2026-06-30',
]

for url in urls:
    request = factory.get(url)
    request.user = user
    try:
        response = view(request)
        print(f"URL: {url} -> Status: {response.status_code}")
    except Exception as e:
        print(f"URL: {url} -> Error!")
        import traceback
        traceback.print_exc()

