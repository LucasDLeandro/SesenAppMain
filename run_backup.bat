@echo off
cd /d "C:\Lucas\SesenAppMain"
REM Ativa o ambiente virtual (ajustar se o nome da pasta for diferente)
if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
)

echo Iniciando rotina de backup do SesenApp...
python manage.py backup_db
echo Backup concluido.
