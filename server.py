"""
Servidor de produção do SesenApp usando Waitress (WSGI).

Este script substitui o 'python manage.py runserver' para uso em produção.
O Waitress é um servidor WSGI puro-Python, estável e seguro para Windows,
que suporta múltiplas conexões simultâneas via threads.

Uso direto:
    python server.py

Uso com PM2:
    pm2 start server.py --name "sesenapp" --interpreter ./env/Scripts/python.exe
"""

import os
import logging

from waitress import serve
from sesen_app.wsgi import application

# Configuração de logging para monitoramento em produção
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)

# Handler para arquivo de log rotativo
file_handler = logging.FileHandler(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'waitress.log'),
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(file_handler)

# Handler para console (visível nos logs do PM2)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(console_handler)

# Configurações do servidor
HOST = '0.0.0.0'
PORT = 8090
THREADS = 8  # Número de threads para atender requisições simultâneas

if __name__ == '__main__':
    logger.info(f'Iniciando SesenApp em http://{HOST}:{PORT}/')
    logger.info(f'Threads de trabalho: {THREADS}')
    logger.info(f'Pressione Ctrl+C para parar (modo manual)')

    serve(
        application,
        host=HOST,
        port=PORT,
        threads=THREADS,
        url_scheme='http',
        channel_timeout=120,        # Timeout de conexão em segundos
        recv_bytes=65536,            # Buffer de recebimento
        send_bytes=18000,            # Buffer de envio
        connection_limit=1000,       # Limite máximo de conexões
        cleanup_interval=30,        # Intervalo de limpeza de conexões inativas
        channel_request_lookahead=0, # Sem lookahead para estabilidade
    )
