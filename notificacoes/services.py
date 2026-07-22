import requests
import os
from dotenv import load_dotenv

load_dotenv()


def auto_message(tel, text):
    
    url = os.environ.get("EVOLUTION_API_URL", "http://127.0.0.1:8080/message/sendText/SESEN")
    
    payload_v1 = {
        "number": tel,
        "text": text
    }
    
    payload_v2 = {
        "number": tel,
        "textMessage": {
            "text": text
        }
    }
    
    headers = {
        "apikey": os.environ.get("EVOLUTION_API_KEY", "teste@2026"),
        "Content-Type": "application/json"
    }

    # Tenta enviar com o formato V1 (usado no servidor de produção)
    response = requests.post(url, json=payload_v1, headers=headers)

    # Se a API reclamar da falta de "textMessage", é porque está rodando a V2 (ex: local)
    if response.status_code == 400 and 'textMessage' in response.text:
        response = requests.post(url, json=payload_v2, headers=headers)

    if response.status_code not in [200, 201]: 
        print(f"FALHA AO ENVIAR ZAP. Status: {response.status_code}, Resposta: {response.text}")
        raise Exception(f"Erro {response.status_code} na API")

    print("Sucesso:", response.text)