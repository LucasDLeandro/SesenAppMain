from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class TransferenciaPatrimonio(models.Model):
    # Relacionamento genérico para apontar para TV, EquipamentoAV ou AparelhoVoip
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    equipamento = GenericForeignKey('content_type', 'object_id')
    
    numero_requisicao = models.CharField(max_length=50, blank=True, null=True, help_text="Número da requisição no sistema corporativo")
    origem = models.CharField(max_length=200, help_text="Local de origem")
    destino = models.CharField(max_length=200, help_text="Local de destino")
    data_transferencia = models.DateTimeField(auto_now_add=True)
    responsavel = models.CharField(max_length=150, help_text="Pessoa responsável pela transferência")
    motivo = models.TextField(blank=True, null=True, help_text="Motivo da transferência")

    def __str__(self):
        return f"Transf {self.numero_requisicao or 'N/A'}: {self.equipamento} ({self.origem} -> {self.destino})"
