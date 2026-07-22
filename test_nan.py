import os, django, datetime, math, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()
from elevadores.views.elev_drf_viewset import ElevadorViewSet
view = ElevadorViewSet()
start = datetime.date(2026, 7, 1)
end = datetime.date(2026, 7, 31)
filtros = {'inicio': start, 'fim': end}
ind_um = view.api_indicador_um(**filtros)
ind_dois = view.api_indicador_dois(**filtros)
ind_tres = view.api_indicador_tres(**filtros)
ind_quatro = view.api_indicador_quatro(**filtros)
grafico_qnt = view.api_totalizacao_elev_grafico_qnt(**filtros)
dados = {'ind_um': ind_um, 'ind_dois': ind_dois, 'ind_tres': ind_tres, 'ind_quatro': ind_quatro, 'totalizacao': grafico_qnt}

def check_nan(obj, path=''):
    if isinstance(obj, float) and math.isnan(obj):
        print(f'FOUND NaN at {path}')
    elif isinstance(obj, dict):
        for k, v in obj.items():
            check_nan(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_nan(v, f'{path}[{i}]')
    elif isinstance(obj, tuple):
        for i, v in enumerate(obj):
            check_nan(v, f'{path}[{i}]')

check_nan(dados, 'root')
