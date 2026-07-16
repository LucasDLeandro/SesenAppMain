from django.db import models
from .remessa_manutencao import RemessaManutencao

class AparelhoManutencao(models.Model):
    remessa = models.ForeignKey(
        RemessaManutencao,
        on_delete=models.CASCADE,
        related_name="aparelhos_manutencao"
    )
    
    patrimonio = models.CharField(
        max_length=10,
        null=True,
    )

    modelo = models.CharField(
        max_length=30,
        null=True,
    )

    fcn = models.CharField(
        max_length=15,
        null=True,
    )

    mac_address = models.CharField(
        max_length=20,
        null=True,
    )

    ramal = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    sala = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    integridade = models.CharField(
        max_length=30,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patrimonio} (Manutenção)"
