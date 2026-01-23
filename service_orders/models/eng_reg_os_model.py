from service_orders.models import *

class EngServiceReg(models.Model):
    os_id=models.AutoField(
        primary_key=True,
    )
    
    categoria=models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        related_name='os_da_categoria'
    )
        
    servico=models.ForeignKey(
        Servico,
        on_delete=models.SET_NULL,
        null=True,
        related_name='os_do_servico'
    )

    descricao=models.TextField(
        null=True,
        blank=True,
    )

    local=models.CharField(
        max_length=15,
        blank=True,
        null=True,
        editable=True
    )

    data_hora_atendimento=models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Data e Horário de Fechamento",
        help_text="Insira a data e horário de conclusão da OS.",
        editable=True,
    )

    supervisor=models.CharField(
        max_length=100,
        blank=True,
        null=True,
        editable=True,
    )
    
    tecnico_responsavel=models.CharField(
        max_length=100,
        blank=True,
        null=True,
        editable=True,
    )

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

