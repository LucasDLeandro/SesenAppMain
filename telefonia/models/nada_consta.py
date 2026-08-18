from django.db import models

class NadaConsta(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
    ]

    protocolo = models.CharField(
        max_length=50, 
        help_text="Protocolo SEI do documento solicitante"
    )
    unidade = models.CharField(
        max_length=200, 
        help_text="Nome completo da unidade solicitante"
    )
    sigla_unidade = models.CharField(
        max_length=20, 
        help_text="Sigla da unidade"
    )
    servidor = models.CharField(
        max_length=200, 
        help_text="Nome completo do servidor"
    )
    data = models.DateTimeField(
        help_text="Data e hora da solicitação"
    )
    
    # Dados preenchidos na conclusão
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pendente'
    )
    ramal = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        help_text="Ramal utilizado pelo servidor"
    )
    email_cadastrado = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        help_text="E-mail cadastrado no sistema de tarifação"
    )
    valor_devido = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00, 
        help_text="Valor devido em R$"
    )
    pdf_fatura = models.FileField(
        upload_to='telefonia/midia/nada_consta/', 
        null=True, 
        blank=True, 
        help_text="Fatura em PDF se houver valor devido"
    )
    tecnico_responsavel = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        help_text="Técnico que concluiu a solicitação"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.protocolo} - {self.servidor}"

    class Meta:
        verbose_name = "Nada Consta"
        verbose_name_plural = "Nada Constas"
        ordering = ['-data']