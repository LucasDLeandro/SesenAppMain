from django.db import models
from .aparelhos_telefonicos import AparelhoVoip

class EmprestimoEvento(models.Model):
    STATUS_CHOICES = [
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído/Recolhido'),
    ]

    evento_nome = models.CharField(max_length=255, help_text="Nome ou descrição do evento")
    data_inicio = models.DateTimeField(help_text="Data e hora de início do empréstimo")
    data_fim = models.DateTimeField(help_text="Data e hora prevista para encerramento e recolhimento")
    solicitante = models.CharField(max_length=255, help_text="Nome do solicitante")
    tecnico_responsavel = models.CharField(max_length=255, null=True, blank=True, help_text="Técnico responsável pela instalação")
    local = models.CharField(max_length=255, help_text="Local de instalação no evento")
    
    aparelhos = models.ManyToManyField(
        AparelhoVoip, 
        related_name='emprestimos_evento',
        blank=True
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_andamento')
    observacoes = models.TextField(null=True, blank=True, help_text="Observações gerais ou motivos de problemas no recolhimento")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.evento_nome} - {self.get_status_display()}"
