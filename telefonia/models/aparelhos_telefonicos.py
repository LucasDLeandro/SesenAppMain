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
        default=IntegridadeAparelho.FUNCIONA
    )

    fcn = models.CharField(max_length=30, null=True, blank=True)
    sala = models.CharField(max_length=50, null=True, blank=True)

    STATUS_CHOICES = [
        ('estoque', 'Em Estoque'),
        ('instalado', 'Instalado'),
        ('manutencao', 'Em Manutenção'),
        ('defeituoso', 'Defeituoso'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='estoque')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patrimonio}"


    