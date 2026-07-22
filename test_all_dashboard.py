import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sesen_app.settings")
django.setup()
from elevadores.views.elev_drf_viewset import ElevadorViewSet
from datetime import datetime, date

v = ElevadorViewSet()
filtros = {
    'inicio': datetime.strptime('2026-07-01', '%Y-%m-%d').date(),
    'fim': datetime.strptime('2026-07-31', '%Y-%m-%d').date()
}

try:
    print("Testando ind_um...")
    v.api_indicador_um(**filtros)
    print("Testando ind_dois...")
    v.api_indicador_dois(**filtros)
    print("Testando ind_tres...")
    v.api_indicador_tres(**filtros)
    print("Testando ind_quatro...")
    v.api_indicador_quatro(**filtros)
    print("Testando totalizacao...")
    v.api_totalizacao_elev_grafico_qnt(**filtros)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
