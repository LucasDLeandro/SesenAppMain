import os
p = r'C:\Lucas\SesenAppMain\notificacoes\services.py'
c = open(p,'r',encoding='utf-8').read()

code = """
def disparar_notificacao_avulso(destinatario, msg_wpp, msg_email, assunto_email="Notificacao Sistema"):
    from django.core.mail import send_mail
    from django.conf import settings
    import threading

    def _send():
        try:
            send_mail(
                subject=assunto_email,
                message=msg_email,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destinatario],
                fail_silently=False,
            )
            print(f"Sucesso ao enviar E-mail para: {destinatario}")
        except Exception as e:
            print(f"ERRO AO ENVIAR E-MAIL (Async): {e}")

    threading.Thread(target=_send).start()
"""

if "def disparar_notificacao_avulso" not in c:
    c = c + code
    open(p,'w',encoding='utf-8').write(c)
    print("Appended disparar_notificacao_avulso to notificacoes.services")
