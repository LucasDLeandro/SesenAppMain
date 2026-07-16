import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()

from reembolsos.models import LimiteReembolso

data = [
    (1, "Diretor-Geral da Secretaria", 466.00),
    (2, "Secretário-Geral da Presidência", 466.00),
    (3, "Assessor-Chefe de Imprensa e Comunicação Social", 466.00),
    (4, "Juiz Auxiliar (em exercício no Tribunal)", 466.00),
    (5, "Secretário", 330.00),
    (6, "Assessor-Chefe", 330.00),
    (7, "Assessor III", 330.00),
    (8, "Servidor (em atividade no interesse do Tribunal e devidamente autorizado pelo Diretor-Geral)", 200.00),
    (9, "Servidor (devidamente autorizado pelo Diretor-Geral com limite especial)", 100.00),
]

for item in data:
    LimiteReembolso.objects.update_or_create(
        indice=item[0],
        defaults={'cargo': item[1], 'valor': item[2]}
    )

print("Limites populados com sucesso!")
