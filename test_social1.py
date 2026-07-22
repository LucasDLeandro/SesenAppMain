import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sesen_app.settings")
django.setup()
from elevadores.models.elev_so_model import ElevadorParadaHistorico

# Buscar registros de paradas para Social 1 ou Social 5
for h in ElevadorParadaHistorico.objects.filter(elevador__icontains='Social 1'):
    print(f"Social 1 -> inicio: {h.data_hora_parada}, fim: {h.data_hora_retorno}, tempo_parado: {h.tempo_parado}")

for h in ElevadorParadaHistorico.objects.filter(elevador__icontains='Social 5'):
    print(f"Social 5 -> inicio: {h.data_hora_parada}, fim: {h.data_hora_retorno}, tempo_parado: {h.tempo_parado}")
