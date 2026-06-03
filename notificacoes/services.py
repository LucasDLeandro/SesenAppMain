import requests


def auto_message(tel, text):
    
    url = "http://127.0.0.1:8080/message/sendText/SESEN"
    
    payload = {
        "number": tel,
        "textMessage": {"text": text}
    }
    headers = {
        "apikey": "teste@2026",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 201: 
        print(f"FALHA AO ENVIAR ZAP. Status: {response.status_code}, Resposta: {response.text}")
        raise Exception(f"Erro {response.status_code} na API")

    print(response.text)