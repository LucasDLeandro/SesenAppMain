@echo off
cd /d "C:\Lucas\SesenAppMain"
REM Ativa o ambiente virtual (ajustar se o nome da pasta for diferente)
if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
)

echo Iniciando rotina de notificacao de eventos...
python manage.py notificar_eventos_expirados
echo Rotina concluida.
