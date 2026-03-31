import requests


def auto_message(tel, text):
    
    url = "http://127.0.0.1:8080/message/sendText/SESEN"

    dict_pessoas = {
        "Samuel": "5561981752513",
        "Andre": "5561985407680",
        "Braitner": "5561984664166",
        "Ione": "5561981840513",
        "Lucas_Maia": "5561992950402",
        "Felipe": "5561984732888",
        "Omerci": "5561983155402"

    }
    
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