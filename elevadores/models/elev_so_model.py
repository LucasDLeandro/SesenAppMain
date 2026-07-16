from elevadores.models import *

class ElevadorStatus(models.Model):
    elevador = models.CharField(
        max_length=50,
        unique=True,
        choices=ELEVATOR_CHOICE,
        verbose_name="Elevador"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_ELEVADOR_CHOICES,
        default='ATIVO',
        verbose_name="Status Atual"
    )
    data_hora_parada = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Parado Desde",
        help_text="Data e hora em que o elevador ficou inoperante."
    )
    programacao = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Programação Especial"
    )
    motivo_programacao = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Motivo da Programação"
    )
    programacao_inicio = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Início da Programação"
    )
    programacao_fim = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fim da Programação"
    )

    def __str__(self):
        return f"{self.elevador} - {self.status}"

class ElevadorParadaHistorico(models.Model):
    elevador = models.CharField(
        max_length=50,
        choices=ELEVATOR_CHOICE,
        verbose_name="Elevador"
    )
    data_hora_parada = models.DateTimeField(
        verbose_name="Data e Hora da Parada"
    )
    data_hora_retorno = models.DateTimeField(
        verbose_name="Data e Hora do Retorno"
    )
    tempo_parado = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas Úteis Parado"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.elevador} parado por {self.tempo_parado} horas"

class ElevOrderReg(models.Model):
    data_hora = models.DateTimeField(
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

    tipo_chamado = models.CharField(
        max_length=20,
        choices=TIPO_CHAMADO_CHOICES,
        default='CORRETIVO',
        verbose_name="Tipo de Chamado",
    )

    elevador = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=ELEVATOR_CHOICE,
        verbose_name="Elevador",
        help_text="Selecione o elevador relacionado à OS.",
    )

    aprisionamento = models.BooleanField(
        null=True, 
        blank=True, 
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
    
    elevador_parado = models.CharField(
        max_length=10,
        null=True, 
        blank=False, 
        choices=STATUS_ELEVADOR_CHOICES, 
        verbose_name="Status do Elevador"
    )

    data_hora_chegada = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data e Horário de Chegada",
        help_text="Insira a data e horário de chegada ao local.",
    )

    data_hora_conclusao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data e Horário de Conclusão",
        help_text="Insira a data e horário de Conclusão.",
    )
    
    tempo_parado = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas Úteis Parado"
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

    status = models.CharField(
        max_length=20,
        choices=STATUS_OS,
        verbose_name="Status",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.protocolo}'


class ManutencaoPreventiva(models.Model):
    STATUS_MPM = [
        ('EXECUTADO', 'Executado'),
        ('INOPERANTE', 'Inoperante'),
        ('NAO_EXECUTADO', 'Não Executado'),
    ]

    elevador = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=ELEVATOR_CHOICE,
        verbose_name="Elevador",
        help_text="Selecione o elevador.",
    )
    
    data_execucao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Execução",
    )
    
    ordem_servico = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Ordem de Serviço",
    )
    
    tecnico = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Executado Por",
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_MPM,
        default='EXECUTADO',
        verbose_name="Status",
    )
    
    qtd_chamado = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Qtd. de Chamados (ICR)",
    )
    
    icr_atingido = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="ICR <= 3",
        help_text="S ou N",
    )
    
    qhp = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="QHP (Horas de Elevador Parado)",
    )
    
    qdu = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="QDU (Dias Úteis)",
    )
    
    ddm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="DDM (%)",
    )
    
    ddm_atingido = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="DDM >= 90%",
        help_text="S ou N",
    )
    
    mes_referencia = models.DateField(
        null=False,
        blank=False,
        verbose_name="Mês de Referência",
        help_text="O mês e ano a qual este relatório pertence (use o dia 1 do mês)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.elevador} - {self.mes_referencia.strftime("%m/%Y")}'

class PecaManutencao(models.Model):
    STATUS_PECA = [
        ('PENDENTE', 'Pendente'),
        ('SUBSTITUIDA', 'Substituída'),
    ]

    elevador = models.CharField(
        max_length=50,
        choices=ELEVATOR_CHOICE,
        verbose_name="Elevador"
    )
    andar = models.CharField(
        max_length=50,
        verbose_name="Andar/Pavimento"
    )
    tipo_peca = models.CharField(
        max_length=100,
        verbose_name="Peça/Componente"
    )
    data_registro = models.DateField(
        auto_now_add=True,
        verbose_name="Data de Registro"
    )
    data_previsao_troca = models.DateField(
        verbose_name="Previsão de Troca"
    )
    
    # Origem
    ordem_servico = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Ordem de Serviço (Origem)"
    )
    tecnico_identificador = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Técnico Identificador"
    )
    
    # Execução
    tecnico = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Técnico Responsável"
    )
    data_efetiva_troca = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data Efetiva da Troca"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_PECA,
        default='PENDENTE',
        verbose_name="Status"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.tipo_peca} - {self.elevador}'