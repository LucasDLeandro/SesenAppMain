from django.db import models

class ContratoColaborador(models.Model):
    numero_contrato = models.CharField(max_length=50, unique=True, verbose_name="Número do Contrato")
    empresa_vinculada = models.CharField(max_length=100, verbose_name="Empresa Vinculada")
    fiscal_contrato = models.CharField(max_length=100, verbose_name="Fiscal do Contrato")
    unidade_fiscal = models.CharField(max_length=200, null=True, blank=True, verbose_name="Unidade de Lotação do Fiscal")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.numero_contrato
