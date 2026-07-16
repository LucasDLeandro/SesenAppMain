from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil

# Cria o inline do Perfil para adicionar dentro da página do User no Admin
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'

from adm_setup.models import ConfiguracaoGeral
from notificacoes.services import auto_message
from django.contrib.auth.forms import AdminUserCreationForm
from django import forms

class CustomUserCreationForm(AdminUserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nome")
    last_name = forms.CharField(max_length=150, required=True, label="Sobrenome")
    email = forms.EmailField(max_length=254, required=True, label="E-mail")
    telefone = forms.CharField(max_length=20, required=True, label="Telefone (WhatsApp)")

    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = AdminUserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'telefone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            perfil, _ = Perfil.objects.get_or_create(user=user)
            perfil.telefone = self.cleaned_data['telefone']
            perfil.save()
            
            # Notifica o novo usuário por e-mail
            from adm_setup.models import ConfiguracaoGeral
            config = ConfiguracaoGeral.get_instance()
            if config.notificar_novos_usuarios:
                try:
                    email_destino = user.email
                    if email_destino:
                        senha = self.cleaned_data.get('password1', '<Senha Oculta>')
                        msg = config.mensagem_boas_vindas.format(
                            usuario=user.username,
                            senha=senha
                        )
                        from django.core.mail import send_mail
                        send_mail(
                            subject='Bem-vindo(a) ao Sistema',
                            message=msg,
                            from_email=None,
                            recipient_list=[email_destino],
                            fail_silently=True,
                        )
                except Exception as e:
                    print(f"Erro ao disparar E-mail de boas vindas: {e}")
                    
        return user

# Define um novo UserAdmin
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Dados Pessoais', {'fields': ('first_name', 'last_name', 'email', 'telefone')}),
    )
    inlines = (PerfilInline,)
    
    def save_related(self, request, form, formsets, change):
        # A superclasse salva os inlines (Perfil)
        super().save_related(request, form, formsets, change)

# Remove o UserAdmin padrão e registra o novo
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
