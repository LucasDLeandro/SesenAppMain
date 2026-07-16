import threading
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime
from telefonia.models import PadraoEmailTelefonia

def enviar_email_boas_vindas_sync(senha_obj):
    if not senha_obj.email:
        return

    from telefonia.views import get_pdf_senha_bytes, get_pdf_tutorial_bytes

    template = PadraoEmailTelefonia.objects.filter(ativo=True).first()
    
    if template:
        assunto = template.assunto
        primeiro_nome = senha_obj.primeiro_nome if senha_obj.primeiro_nome else "Usuário"
        
        mensagem = template.corpo
        mensagem = mensagem.replace("{primeiro_nome}", primeiro_nome)
        mensagem = mensagem.replace("{senha}", senha_obj.senha or "N/A")
        
        if template.assinatura:
            mensagem += f"\n\n{template.assinatura}"
    else:
        assunto = "Bem-vindo(a) ao SESEN - Telefonia"
        mensagem = f"Olá {senha_obj.usuario or 'Usuário'},\nSua senha telefônica é: {senha_obj.senha or 'N/A'}"

    # Obter os bytes dos PDFs
    pdf_senha_bytes = get_pdf_senha_bytes(senha_obj.pk)
    pdf_tutorial_bytes = get_pdf_tutorial_bytes()

    bcc_list = []
    if template and template.email_copia:
        bcc_list.append(template.email_copia)

    email = EmailMessage(
        subject=assunto,
        body=mensagem,
        from_email=settings.EMAIL_HOST_USER,
        to=[senha_obj.email],
        bcc=bcc_list if bcc_list else None,
    )

    if pdf_senha_bytes:
        nome_usuario = senha_obj.usuario or f"senha_{senha_obj.ramal or 'telefonia'}"
        email.attach(f"{nome_usuario}.pdf", pdf_senha_bytes, 'application/pdf')
    
    if pdf_tutorial_bytes:
        data_atual = datetime.now().strftime("%d-%m-%Y")
        email.attach(f"00tutorial novas senhas {data_atual}.pdf", pdf_tutorial_bytes, 'application/pdf')

    try:
        email.send(fail_silently=False)
        print(f"E-mail de boas vindas enviado com sucesso para {senha_obj.email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail de boas vindas: {e}")

def enviar_email_boas_vindas_async(senha_obj):
    thread = threading.Thread(target=enviar_email_boas_vindas_sync, args=(senha_obj,))
    thread.start()
