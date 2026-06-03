from elevadores.models import *

class RegistroParadaElev(models.Model):
    os_origem=models.ForeignKey(
        ElevOrderReg, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='historico_paradas')
    
    data_hora_parada=models.DateTimeField()

    data_hora_reativacao=models.DateTimeField(null=True, blank=True)

    motivo_pendencia=models.CharField(
        max_length=600,
        null=True,
        blank=True
    )

created_at=models.DateTimeField(auto_now_add=True)
updated_at=models.DateTimeField(auto_now=True)

def __str__(self):
    return f"{self.os_origem}"