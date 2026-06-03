from django.db import models



#Choices para o campo de status
class StatusSolicitacao(models.TextChoices):
    RECEBIDA = 'recebida', 'Recebida'
    EM_ANALISE = 'em_analise', 'Em Análise'
    PENDENTE = 'pendente', 'Pendente'
    CONCLUIDA = 'concluida', 'Concluída'

class IntegridadeAparelho(models.TextChoices):

    PERFEITO = 'perfeito', 'Perfeito'
    BOM_ESTADO = 'bom_estado', 'Bom Estado'
    REGULAR = 'regular', 'Regular'
    RUIM = 'ruim', 'Ruim'
    CRITICO = 'critico', 'Crítico'

DESVIO_CHOICES = [
    (True, 'Sim'),
    (False, 'Não')
]

from .solicitacao_aparelho import TelefoneSolicitacao
from .aparelhos_telefonicos import AparelhoVoip
from .aparelhos_defeito import AparelhoDefeito
