from elevadores.models import *

class TrocaPecas(models.Model):
    os_origem=models.ForeignKey(
        ElevOrderReg,
        on_delete=models.SET_NULL,
        null=True,
    )
    componente=models.CharField(
        max_length=500,
        null=True
    )
    sub_componente=models.CharField(
        max_length=500,
        null=True
    )
    estimativa_troca=models.DateTimeField(null=True, blank=True)
    tecnico_solicitane=models.CharField(max_length=200)
    data_troca=models.DateTimeField(null=True,)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
