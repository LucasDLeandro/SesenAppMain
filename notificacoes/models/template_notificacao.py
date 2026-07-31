from notificacoes.models import *

class TemplateMessage(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('false', '---'),
        ('os_elev_registro', 'Elevadores - Registro de Nova OS'),
        ('os_elev_conclusao', 'Elevadores - Conclusão de OS Aberta'),
        ('tel_solicitacao_aparelho', 'Telefonia - Solicitação de Aparelho'),
        ('tel_solicitacao_senha', 'Telefonia - Solicitação de Senha'),
        ('tel_recolhimento_evento', 'Telefonia - Recolhimento de Aparelho em Evento'),
        ('os_elev_andamento', 'Elevadores - OS em Andamento' ),
        ('os_elev_conclusao_peca', 'Elevadores - Conclusão de OS c/ Troca de Peça'),
        ('os_elev_aguardando_peca_parado', 'Elevadores - OS Aguardando Peça (Elev. Parado)'),
        ('os_elev_aguardando_peca_ativo', 'Elevadores - OS Aguardando Peça (Elev. Funcionando)'),
        ('VAGO_5', 'Elevadores - TEMPLATE VAGO - 5', ),
        ('VAGO_6', 'Elevadores - TEMPLATE VAGO - 6', )
    ]

    tipo_evento = models.CharField(
        max_length=80,
        choices=TIPO_EVENTO_CHOICES,
        unique=True,
        verbose_name="Gatilho / Situação"
    )

    id_template=models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Identificador do Template"
    )

    base_text=models.TextField(
        default="Prezado(a), {nome}\n\n"
            "Seguem as informações sobre a abertura do chamado para a empresa Otis:\n\n"
            "Atendente OTIS: {atendente}\n"
            "Data/Hora: {data_hora}\n"
            "Elevador: {elevador}\n"
            "Ocorrência: {ocorrencia}\n"
            "Protocolo: {protocolo}\n"
            "Solicitante: {solicitante}"
    )

    contatos=models.ManyToManyField(
        'Contato',
        related_name='regras_notificacao',
        blank=True
    )

    is_ativo=models.BooleanField(
        default=True,
        verbose_name="Template Ativo?"
    )

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id_template}"