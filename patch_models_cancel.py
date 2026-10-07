import re

with open(r'C:\Lucas\SesenAppMain\telefonia\models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add to SolicitacaoAparelhoLinha
if 'justificativa_cancelamento' not in content[content.find('class SolicitacaoAparelhoLinha'):content.find('class SolicitacaoSenha')]:
    content = content.replace(
        "    tecnico_responsavel = models.CharField(max_length=255, blank=True, null=True)\n",
        "    tecnico_responsavel = models.CharField(max_length=255, blank=True, null=True)\n    justificativa_cancelamento = models.TextField(blank=True, null=True)\n    cancelado_por = models.CharField(max_length=255, blank=True, null=True)\n    data_cancelamento = models.DateTimeField(blank=True, null=True)\n"
    )

# Add to SolicitacaoSenha
# Find class SolicitacaoSenha
idx_senha = content.find('class SolicitacaoSenha(models.Model):')
if 'justificativa_cancelamento' not in content[idx_senha:content.find('class NadaConsta')]:
    # Replace the first tecnico_responsavel after idx_senha
    rep1 = "    tecnico_responsavel = models.CharField(max_length=255, blank=True, null=True)\n"
    rep2 = "    tecnico_responsavel = models.CharField(max_length=255, blank=True, null=True)\n    justificativa_cancelamento = models.TextField(blank=True, null=True)\n    cancelado_por = models.CharField(max_length=255, blank=True, null=True)\n    data_cancelamento = models.DateTimeField(blank=True, null=True)\n"
    content = content[:idx_senha] + content[idx_senha:].replace(rep1, rep2, 1)

# Add to NadaConsta
idx_nada = content.find('class NadaConsta(models.Model):')
if 'justificativa_cancelamento' not in content[idx_nada:]:
    rep1 = "    tecnico_responsavel = models.CharField(max_length=255, blank=True, null=True)\n"
    rep2 = "    tecnico_responsavel = models.CharField(max_length=255, blank=True, null=True)\n    justificativa_cancelamento = models.TextField(blank=True, null=True)\n    cancelado_por = models.CharField(max_length=255, blank=True, null=True)\n    data_cancelamento = models.DateTimeField(blank=True, null=True)\n"
    content = content[:idx_nada] + content[idx_nada:].replace(rep1, rep2, 1)

# NadaConsta needs 'cancelada' in STATUS_CHOICES
if "('cancelada', 'Cancelada')" not in content[idx_nada:content.find('status = models.CharField', idx_nada)]:
    old_status = "        ('concluida', 'Concluída'),\n    ]"
    new_status = "        ('concluida', 'Concluída'),\n        ('cancelada', 'Cancelada'),\n    ]"
    content = content[:idx_nada] + content[idx_nada:].replace(old_status, new_status, 1)


with open(r'C:\Lucas\SesenAppMain\telefonia\models.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Models patched!")
