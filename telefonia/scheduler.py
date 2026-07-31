import logging
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from telefonia.tasks import verificar_e_notificar_eventos

logger = logging.getLogger(__name__)

def start():
    # Evita que o scheduler seja iniciado mais de uma vez quando o Django usa o auto-reloader (runserver)
    if os.environ.get('RUN_MAIN') != 'true' and 'runserver' in sys.argv:
        return

    scheduler = BackgroundScheduler()
    
    # Adiciona a tarefa para rodar a cada 60 minutos
    scheduler.add_job(verificar_e_notificar_eventos, 'interval', minutes=60, id='job_notificar_eventos_expirados', replace_existing=True)
    
    # scheduler.start() precisa ser executado, mas com cautela em produção se houver vários workers.
    scheduler.start()
    logger.info("APScheduler iniciado: tarefa 'verificar_e_notificar_eventos' configurada para rodar a cada 60 minutos.")
