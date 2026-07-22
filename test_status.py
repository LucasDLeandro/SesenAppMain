import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sesen_app.settings")
django.setup()
from elevadores.models.elev_so_model import ElevadorStatus, ElevadorParadaHistorico

# Check status
print("STATUS:")
for e in ElevadorStatus.objects.all():
    if 'Social 1' in e.elevador or 'Social 5' in e.elevador:
        print(f"{e.elevador} -> {e.status}, parada: {e.data_hora_parada}")

print("\nPARADAS ABERTAS:")
for p in ElevadorParadaHistorico.objects.filter(data_hora_retorno__isnull=True):
    print(f"{p.elevador} -> inicio: {p.data_hora_parada}")
