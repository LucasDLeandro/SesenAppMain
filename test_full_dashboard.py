import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sesen_app.settings")
django.setup()
from rest_framework.test import APIRequestFactory
from elevadores.views.elev_drf_viewset import ElevadorViewSet

factory = APIRequestFactory()
request = factory.get('/elevadores/api/elevadoress/dashboard/', {'inicio': '2026-07-01', 'fim': '2026-07-31'})

v = ElevadorViewSet()
try:
    response = v.dashboard(request)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
