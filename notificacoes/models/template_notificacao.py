from notificacoes.models import *

class TemplateMessage(models.Model):
    id_message=models.CharField(
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
        return f"{self.id_message}"