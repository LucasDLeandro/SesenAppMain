from telefonia.models import *

class StatusSenha(models.TextChoices):
    RECEBIDA = 'recebida', 'Recebida'
    AGUARDANDO_SUPERVISOR = 'aguardando_supervisor', 'Aguardando Supervisor'
    FINALIZADA = 'finalizada', 'Finalizada'

class CriarSenha(models.Model):
    protocolo = models.CharField(
        max_length=20,
        null=True,
        help_text="Protocolo SEI do Documento",
        editable=True,
    )

    unidade = models.CharField(
        max_length=200,
        null=True,
    )

    sigla_unidade = models.CharField(
        max_length=20,
        null=True,
    )

    ramal = models.CharField(
        max_length=10,
        null=True,
    )

    primeiro_nome = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    sobrenome = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    
    cargo = models.CharField(
        max_length=20,
        choices=[('servidor', 'Servidor'), ('colaborador', 'Colaborador')],
        default='servidor'
    )
    
    numero_contrato = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Apenas para Colaboradores"
    )
    
    empresa_vinculada = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Apenas para Colaboradores"
    )
    
    fiscal_contrato = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Apenas para Colaboradores"
    )

    unidade_fiscal = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Unidade de Lotação do Fiscal (Apenas Colaboradores)"
    )

    @property
    def usuario(self):
        nome = self.primeiro_nome or ""
        sobrenome = self.sobrenome or ""
        return f"{nome} {sobrenome}".strip() or "N/A"

    email = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
        help_text="E-mail Institucional"
    )

    senha = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Senha registrada"
    )

    edificios = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default="Ed. Sede/Anexo",
        help_text="Edifícios onde pode ser utilizada"
    )

    solicitante = models.CharField(
        max_length=100,
        null=True,
        help_text= "Nome de quem assinou o pedido",
    )

    categoria = models.CharField(
        max_length=10,
        null=True,
    )

    desvio = models.BooleanField(
        choices=DESVIO_CHOICES,
        default=False
    )

    tel_desvio_externo = models.CharField(
        max_length = 30,
        null=True,
        blank=True
    )

    nome_tecnico = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=StatusSenha.choices,
        default=StatusSenha.RECEBIDA,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.ramal}"
