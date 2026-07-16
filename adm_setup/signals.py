from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models
import re

# Lista de apps que o Signal irá monitorar e limpar
APPS_TO_CLEAN = [
    'empresas', 'equipe_tecnica', 'telefonia', 'audiovideo',
    'gestao_patrimonio', 'reembolsos', 'usuarios', 'notificacoes', 
    'clientes', 'contratos', 'elevadores', 'adm_setup'
]

# Campos que devem receber formatação Title Case
TITLE_CASE_FIELDS = [
    'nome', 'nome_empresa', 'nome_contato', 'nome_solicitante', 
    'rua', 'bairro', 'cidade', 'solicitante', 'marca', 'modelo', 
    'tecnico', 'responsavel', 'primeiro_nome', 'sobrenome'
]

# Campos que devem ter toda pontuação removida (manter apenas dígitos)
DIGITS_ONLY_FIELDS = [
    'cpf', 'cnpj', 'cep', 'telefone', 'whatsapp', 'celular'
]

# Campos que devem remover caracteres estranhos (manter letras e números) e Uppercase
ALPHANUM_ONLY_FIELDS = [
    'rg', 'mac_address', 'fcn'
]

# Campos que devem forçar Caixa Alta (Uppercase)
UPPERCASE_FIELDS = [
    'patrimonio', 'protocolo', 'protocolo_sei', 'sigla', 'sigla_unidade', 'local'
]

@receiver(pre_save)
def clean_model_data(sender, instance, **kwargs):
    # Verifica se o modelo pertence a uma das nossas apps
    if getattr(sender._meta, 'app_label', None) not in APPS_TO_CLEAN:
        return
        
    for field in sender._meta.fields:
        if isinstance(field, (models.CharField, models.TextField, models.EmailField)):
            val = getattr(instance, field.name, None)
            
            if isinstance(val, str) and val.strip() != "":
                # 1. Strip whitespaces
                val = val.strip()
                
                field_name = field.name.lower()
                
                # 2. Lowercase emails
                if isinstance(field, models.EmailField) or 'email' in field_name:
                    val = val.lower()
                
                # 3. Handle specific formatting based on field name rules
                elif field_name in DIGITS_ONLY_FIELDS:
                    val = re.sub(r'\D', '', val)
                    
                elif field_name in ALPHANUM_ONLY_FIELDS:
                    val = re.sub(r'[^a-zA-Z0-9]', '', val).upper()
                    
                elif field_name in UPPERCASE_FIELDS:
                    val = val.upper()
                    
                elif field_name in TITLE_CASE_FIELDS or 'nome' in field_name:
                    words = val.split()
                    exceptions = ['de', 'da', 'do', 'das', 'dos', 'e']
                    title_words = []
                    for i, w in enumerate(words):
                        # Evita TitleCase se a palavra for uma preposição comum (exceto no início do nome)
                        if w.lower() in exceptions and i > 0:
                            title_words.append(w.lower())
                        else:
                            # Título básico: primeira maiúscula, resto minúscula
                            title_words.append(w.capitalize())
                    val = " ".join(title_words)
                
                # 4. Atualiza o valor na instância
                setattr(instance, field.name, val)
