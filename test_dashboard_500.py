import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sesen_app.settings")
django.setup()
from elevadores.views.elev_drf_viewset import ElevadorViewSet
from datetime import datetime, date

v = ElevadorViewSet()
try:
    v.api_indicador_quatro(inicio=datetime.strptime('2026-07-01', '%Y-%m-%d').date(), fim=datetime.strptime('2026-07-31', '%Y-%m-%d').date())
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
