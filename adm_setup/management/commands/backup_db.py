import os
import sys
import gzip
import shutil
import subprocess
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Cria um backup completo do banco de dados MySQL e aplica a política de retenção.'

    def handle(self, *args, **kwargs):
        # 1. Obter as configurações do banco de dados
        db_settings = settings.DATABASES['default']
        db_name = db_settings.get('NAME')
        db_user = db_settings.get('USER')
        db_password = db_settings.get('PASSWORD')
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '3306')
        
        # 2. Configurar o diretório de backups
        # Cria a pasta 'backups' na raiz do projeto, caso não exista
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # 3. Gerar o nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sql_filename = f"backup_{db_name}_{timestamp}.sql"
        sql_filepath = os.path.join(backup_dir, sql_filename)
        gz_filepath = f"{sql_filepath}.gz"
        
        # 4. Executar o mysqldump
        self.stdout.write(self.style.NOTICE(f'Iniciando backup do banco de dados: {db_name}...'))
        
        # Procura o executável do mysqldump
        mysqldump_exe = 'mysqldump'
        fallback_path = r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe'
        if os.name == 'nt':
            if shutil.which('mysqldump') is None:
                if os.path.exists(fallback_path):
                    mysqldump_exe = fallback_path
                else:
                    self.stderr.write(self.style.ERROR('O comando "mysqldump" não foi encontrado no PATH do sistema e não está no caminho padrão.'))
                    if os.path.exists(sql_filepath):
                        os.remove(sql_filepath)
                    sys.exit(1)

        dump_cmd = [
            mysqldump_exe,
            f'--user={db_user}',
            f'--password={db_password}',
            f'--host={db_host}',
            f'--port={db_port}',
            db_name
        ]
        
        try:
            with open(sql_filepath, 'w', encoding='utf-8') as f:
                subprocess.run(dump_cmd, stdout=f, check=True)
            self.stdout.write(self.style.SUCCESS('Dump SQL gerado com sucesso.'))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f'Erro ao executar mysqldump: {e}'))
            if os.path.exists(sql_filepath):
                os.remove(sql_filepath)
            sys.exit(1)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR('O comando "mysqldump" não foi encontrado no PATH do sistema.'))
            if os.path.exists(sql_filepath):
                os.remove(sql_filepath)
            sys.exit(1)
            
        # 5. Comprimir o arquivo .sql para .sql.gz
        self.stdout.write(self.style.NOTICE('Comprimindo o arquivo de backup...'))
        try:
            with open(sql_filepath, 'rb') as f_in:
                with gzip.open(gz_filepath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Remove o arquivo SQL não comprimido
            os.remove(sql_filepath)
            self.stdout.write(self.style.SUCCESS(f'Backup comprimido gerado em: {gz_filepath}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao comprimir o arquivo: {e}'))
            sys.exit(1)
            
        # 6. Política de retenção (Ex: 365 dias)
        dias_retencao = 365
        self.stdout.write(self.style.NOTICE(f'Limpando backups antigos (retenção de {dias_retencao} dias)...'))
        
        cutoff_date = datetime.now() - timedelta(days=dias_retencao)
        deleted_count = 0
        
        for filename in os.listdir(backup_dir):
            if filename.startswith('backup_') and filename.endswith('.sql.gz'):
                file_path = os.path.join(backup_dir, filename)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff_date:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        self.stdout.write(f"Backup removido: {filename}")
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f'Falha ao remover arquivo {filename}: {e}'))
                        
        self.stdout.write(self.style.SUCCESS(f'Rotina concluída. {deleted_count} backup(s) antigo(s) removido(s).'))
