from telefonia.models import *

class AparelhoVoip(models.Model):
    patrimonio = models.CharField(
        max_length=10,
        null=True,
    )

    modelo = models.CharField(
        max_length=30,
        null=True,
    )

    mac_address = models.CharField(
        max_length=20,
        null=True,
    )

    ramal = models.CharField(
        max_length=10,
        null=True,
    )

    integridade = models.CharField(
        max_length=30,
        null=True,
        choices=IntegridadeAparelho.choices,
        default=IntegridadeAparelho.PERFEITO
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patrimonio}"


    