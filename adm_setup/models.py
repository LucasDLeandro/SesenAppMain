from django.db import models

class ConfiguracaoGeral(models.Model):
    notificar_novos_usuarios = models.BooleanField(
        default=False,
        verbose_name="Notificar novos usuários via E-mail"
    )
    mensagem_boas_vindas = models.TextField(
        default="Olá, seja bem-vindo ao SesenApp!\nSeu usuário é: {usuario}\nSua senha padrão é: {senha}\n\nVocê deverá trocar sua senha no primeiro login.",
        verbose_name="Mensagem de Boas-Vindas",
        help_text="Utilize {usuario} e {senha} para injetar os dados dinamicamente."
    )

    def save(self, *args, **kwargs):
        # Garante que seja um Singleton (apenas 1 registro no banco)
        self.pk = 1
        super(ConfiguracaoGeral, self).save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Configuração Geral"
        verbose_name_plural = "Configurações Gerais"

class AgendamentoTask(models.Model):
    task_id = models.CharField(max_length=100, unique=True, verbose_name="ID da Tarefa")
    nome_amigavel = models.CharField(max_length=150, verbose_name="Nome da Rotina")
    intervalo_minutos = models.IntegerField(default=60, verbose_name="Intervalo em Minutos")
    ativo = models.BooleanField(default=True, verbose_name="Status (Ativo/Inativo)")

    def __str__(self):
        return f"{self.nome_amigavel} ({self.intervalo_minutos} min)"
