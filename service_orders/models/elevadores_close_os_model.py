from service_orders.models import *

class ElevOrderClose(models.Model):
    protocolo = models.OneToOneField(
        ElevOrderReg, 
        on_delete=models.CASCADE,
        limit_choices_to={'status': 'ABERTA'},
        verbose_name="Protocolo",)
    
    data_hora_chegada = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name="Data e Horário de Chegada",
        help_text="Insira a data e horário de chegada ao local.",
    )

    data_hora_saida = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name="Data e Horário de Saída",
        help_text="Insira a data e horário de saída do local.",
    )

    tecnico = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        default="",
        verbose_name="Técnico Responsável",
        help_text="Insira o nome do técnico responsável pelo atendimento.",
    )

    servico = models.CharField(
        max_length=600,
        null=False,
        blank=True,
        default="",
        verbose_name="Serviço Executado",
        help_text="Descreva a solução aplicada na OS.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.protocolo}"
    
    