from django.db import models


class RemessaManutencao(models.Model):
    memorando = models.CharField(
        max_length=100,
        help_text="Nº do Memorando (ex: Memorando SESEN/COSEN/SAD nº 142/2026)"
    )
    
    data_remessa = models.DateTimeField(auto_now_add=True)
    
    empresa_contratada = models.CharField(
        max_length=200,
        default="3CORP TECHNOLOGY LTDA."
    )
    
    contrato_tse = models.CharField(
        max_length=100,
        default="Contrato TSE nº 40/2021"
    )



    def __str__(self):
        return f"{self.memorando}"
