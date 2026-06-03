from telefonia.models import *

class CriarSenha(models.Model):
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

    ramal = models.CharField(
        max_length=10,
        null=True,
    )

    usuario = models.CharField(
        max_length=30,
        null=True,
    )

    solicitante = models.CharField(
        max_length=100,
        null=True,
        help_text= "Nome de quem assinou o pedido",
    )

    categoria = models.CharField(
        max_length=10,
        null=True,
    )

    desvio = models.BooleanField(
        choices=DESVIO_CHOICES,
        default=False
    )

    tel_desvio_externo = models.CharField(
        max_length = 30,
        null=True
    )

    nome_tecnico = models.CharField(
        max_length=100,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.ramal}"
