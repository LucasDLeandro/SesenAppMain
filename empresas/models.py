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
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="contatos")
    nome_contato = models.CharField(max_length=255, verbose_name="Nome do Contato")
    cargo = models.CharField(max_length=150, blank=True, null=True, verbose_name="Cargo")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    whatsapp = models.CharField(max_length=20, blank=True, null=True, verbose_name="WhatsApp")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome_contato} - {self.empresa.nome_empresa}"
