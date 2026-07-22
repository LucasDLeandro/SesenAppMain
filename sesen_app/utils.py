import os
import uuid
from datetime import datetime

def dinamic_upload_path(instance, filename):
    """
    Salva o arquivo no formato: media/<nome_do_app>/<nome_da_tabela>/<ano>/<mes>/<uuid>_nome_original
    """
    app_name = instance._meta.app_label
    table_name = instance._meta.model_name
    
    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
    
    hoje = datetime.now()
    ano = hoje.strftime("%Y")
    mes = hoje.strftime("%m")
    
    caminho = os.path.join(app_name, table_name, ano, mes, unique_filename)
    
    return caminho
