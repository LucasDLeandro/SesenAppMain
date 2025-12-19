from service_orders.models import *

class ServiceOrder(models.Model):
    data_hora = models.DateTimeField(
        null=False, 
        blank=False, 
        verbose_name="Data e Horário do Registro",
        help_text="Insira a data e horário do registro da OS.",
        editable=True,
    )

    protocolo = models.CharField(
        max_length=20, 
        unique=True, 
        null=False, 
        blank=False, 
        verbose_name="Protocolo", 
        help_text="Digite o protocolo da OS, ex: 123456789...", 
        editable=True, 
        error_messages= {
            'unique': "Este protocolo já existe. Por favor, verifique e tente novamente.",
            'blank': "O campo não pode estar vazio. Por favor, insira o protocolo da OS.",
            'null': "O campo não pode ser nulo. Por favor, insira o protocolo da OS.",
            'max_length': "O protocolo excedeu o número máximo de caracteres permitidos (20).",
        }
    )

    elevador = models.IntegerField(
        null=False,
        blank=False,
        choices=ELEVATOR_CHOICE,
        verbose_name="Elevador",
        help_text="Selecione o elevador relacionado à OS.",
    )

    aprisionamento = models.BooleanField(
        null=True, 
        blank=False, 
        default=None, 
        verbose_name="Aprisionamento",
    )

    ocorrencia = models.CharField(
        max_length=600, 
        null=False, 
        blank=True, 
        verbose_name="Ocorrência",
        help_text="Descreva a ocorrência relacionada à OS.",)
    

    atendente = models.CharField(
        max_length=200, 
        null=False, 
        blank=False, 
        default="",
        verbose_name="Atendente",
        )
    solicitante = models.CharField(
        max_length=200, 
        null=False, 
        blank=False, 
        default="",
        verbose_name="Solicitante",
        )
    
    elevador_parado = models.IntegerField(
        null=False, 
        blank=False, 
        choices=STATUS_ELEVADOR_CHOICES, 
        default=1,
        verbose_name="Status do Elevador"
    )

    status = models.CharField(
        null=False,
        blank=False,
        verbose_name="Status",
        default='ABERTA'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.protocolo