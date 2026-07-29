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

def auto_email(destinatario, assunto, texto):
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        send_mail(
            subject=assunto,
            message=texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False,
        )
        print(f"Sucesso ao enviar E-mail para: {destinatario}")
    except Exception as e:
        print(f"FALHA AO ENVIAR E-MAIL. Erro: {e}")
        raise Exception(f"Erro ao enviar E-mail: {e}")

def disparar_notificacao_contato(contato, texto_zap, texto_email, assunto_email):
    """
    Função de conveniência que roteia a mensagem para WhatsApp e/ou E-mail 
    baseado nas flags ativas do objeto Contato.
    """
    # 1. Disparo de WhatsApp
    if contato.receber_whatsapp:
        import re
        telefone = getattr(contato, '_telefone_sanitizado', contato.telefone)
        if telefone:
            telefone = re.sub(r'\D', '', telefone)
            if len(telefone) in (10, 11) and not telefone.startswith('55'):
                telefone = f"55{telefone}"
            
            try:
                auto_message(telefone, texto_zap)
            except Exception as e:
                print(f"Erro disparando WhatsApp para {contato.nome}: {e}")
                
    # 2. Disparo de E-mail
    if contato.receber_email:
        email = getattr(contato.pessoa, 'email', None) if contato.pessoa else None
        if email:
            try:
                auto_email(email, assunto_email, texto_email)
            except Exception as e:
                print(f"Erro disparando E-mail para {contato.nome}: {e}")