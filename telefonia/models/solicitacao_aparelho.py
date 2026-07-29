from telefonia.models import *

class TelefoneSolicitacao(models.Model):
    data = models.DateTimeField(
        help_text="Data e Hora que a solicitação chegou na seção",
        editable=True,
    )

    protocolo = models.CharField(
        max_length=20,
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

    ramal = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    
    local = models.CharField(
        max_length=255,
        null=True,
    )

    qnt_solicitada = models.IntegerField()

    solicitante = models.CharField(
        max_length=100,
        help_text= "Nome de quem assinou o pedido",
    )

    tecnico_responsavel = models.CharField(
        max_length=200,
        null=True,
    )

    relatorio = models.CharField(
        max_length=500,
        null=True,
    )

    autorizacao_sad = models.CharField(
        max_length=20,
        null=True,
        help_text="Protocolo SEI do Documento que autoriza a instalação",
        editable=True,
    )

    data_instalacao = models.DateTimeField(
        null=True,
        blank=True
    )

    termo_transferencia_interna = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    aparelhos = models.ManyToManyField(
        'AparelhoVoip',
        blank=True,
        related_name='solicitacoes'
    )

    status = models.CharField(
        max_length=20,
        null=True,
        choices=StatusSolicitacao.choices,
        default=StatusSolicitacao.RECEBIDA,
    )

    midia = models.FileField(
        upload_to='telefonia/midia/solicitacoes/',
        null=True,
        blank=True,
        help_text="Anexo ou mídia para a solicitação"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.protocolo}"