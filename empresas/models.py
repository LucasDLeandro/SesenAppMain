from django.db import models

class Empresa(models.Model):
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    nome_empresa = models.CharField(max_length=255, verbose_name="Nome da Empresa")
    classificacao = models.CharField(max_length=150, blank=True, null=True, verbose_name="Classificação/Ramo")
    cargo = models.CharField(max_length=150, blank=True, null=True, verbose_name="Cargo/Função Principal")
    
    # Endereço
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    rua = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rua")
    numero = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número")
    bairro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    
    # Geolocalização (preparado para API futura)
    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome_empresa} ({self.cnpj})"

class ContatoEmpresa(models.Model):
    pessoa = models.ForeignKey('usuarios.Pessoa', on_delete=models.CASCADE, null=True, blank=True, related_name='contato_empresas')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="contatos")
    cargo = models.CharField(max_length=150, blank=True, null=True, verbose_name="Cargo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.pessoa:
            return f"{self.pessoa.nome} - {self.empresa.nome_empresa}"
        return f"Contato Sem Pessoa - {self.empresa.nome_empresa}"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ContatoEmpresa)
def sincronizar_contato_profissional(sender, instance, created, **kwargs):
    """
    Ao criar ou atualizar um ContatoEmpresa, se houver uma pessoa vinculada,
    garante que essa mesma pessoa possua um registro em Profissional para
    poder ser alocada em Contratos.
    """
    if instance.pessoa:
        from contratos.models import Profissional
        Profissional.objects.get_or_create(pessoa=instance.pessoa)

