from telefonia.models import *

class TelefoneSolicitacao(models.Model):
    data = models.DateTimeField(
        help_text="Data e Hora que a solicitação chegou na seção",
        editable=True,
    )

    protocolo = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        help_text="Protocolo SEI do Documento",
        editable=True,
    )

    unidade = models.CharField(
        max_length=200,
        null=True,
    )

    sigla_unidade = models.CharField(
        max_length=20,
        null=True,
    )
    
    local = models.CharField(
        max_length=20,
        null=True,
    )

    qnt_solicitada = models.IntegerField()

    solicitante = models.CharField(
        max_length=100,
        help_text= "Nome de quem assinou o pedido",
    )

    tecnico_avaliou = models.CharField(
        max_length=200,
        null=True,
    )

    avaliacao = models.CharField(
        max_length=500,
        null=True,
    )

    autorizacao_sad = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        help_text="Protocolo SEI do Documento que autoriza a instalação",
        editable=True,
    )

    tecnico_instalou = models.CharField(
        max_length=100,
        null=True
    )

    status = models.CharField(
        max_length=20,
        null=True,
        choices=StatusSolicitacao.choices,
        default=StatusSolicitacao.RECEBIDA,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.protocolo}"