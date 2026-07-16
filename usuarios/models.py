from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class TiposUsuario(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrador'
    SUPERVISOR = 'SUPERVISOR', 'Supervisor'
    TECNICO = 'TECNICO', 'Técnico'
    VISUALIZACAO = 'VISUALIZACAO', 'Visualização'

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo = models.CharField(
        max_length=20,
        choices=TiposUsuario.choices,
        default=TiposUsuario.VISUALIZACAO,
        verbose_name="Tipo de Usuário"
    )
    precisa_trocar_senha = models.BooleanField(
        default=True,
        verbose_name="Precisa trocar senha no próximo login"
    )
    telefone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Telefone (WhatsApp)"
    )
    email_boas_vindas_enviado = models.BooleanField(
        default=False,
        verbose_name="E-mail de boas-vindas enviado"
    )
    email_boas_vindas_erro = models.TextField(
        blank=True,
        null=True,
        verbose_name="Erro de envio do e-mail"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_display()}"

    @property
    def is_admin(self):
        return self.tipo == TiposUsuario.ADMIN

    @property
    def is_supervisor(self):
        return self.tipo == TiposUsuario.SUPERVISOR

    @property
    def is_tecnico(self):
        return self.tipo == TiposUsuario.TECNICO

    @property
    def is_visualizacao(self):
        return self.tipo == TiposUsuario.VISUALIZACAO


