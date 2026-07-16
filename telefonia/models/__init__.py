from django.db import models

#Choices para o campo de status
class StatusSolicitacao(models.TextChoices):
    RECEBIDA = 'recebida', 'Recebida'
    EM_ANALISE = 'em_analise', 'Em Análise'
    PENDENTE = 'pendente', 'Pendente'
    CONCLUIDA = 'concluida', 'Concluída'

class IntegridadeAparelho(models.TextChoices):
    FUNCIONA = 'funciona', 'Funciona'
    DEFEITO = 'defeito', 'Defeito'

DESVIO_CHOICES = [
    (True, 'Sim'),
    (False, 'Não')
]

from .solicitacao_aparelho import TelefoneSolicitacao
from .aparelhos_telefonicos import AparelhoVoip
from .remessa_manutencao import RemessaManutencao
from .solicitacao_senha import CriarSenha
from .contrato_colaborador import ContratoColaborador
from .aparelhos_manutencao import AparelhoManutencao
from .padrao_senha import PadraoSenhaTelefonia
from .padrao_tutorial import PadraoTutorialTelefonia
from .padrao_email import PadraoEmailTelefonia
