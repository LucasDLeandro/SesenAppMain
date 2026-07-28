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


class Pessoa(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pessoa_vinculada')
    nome = models.CharField(max_length=255, verbose_name="Nome")
    sobrenome = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sobrenome")
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True, verbose_name="CPF")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.sobrenome:
            return f"{self.nome} {self.sobrenome}"
        return self.nome

class FormacaoProfissional(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='formacoes')
    titulo = models.CharField(max_length=255, verbose_name="Formação/Título")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
