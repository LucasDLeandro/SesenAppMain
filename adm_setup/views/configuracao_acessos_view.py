from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from equipe_tecnica.models import PadraoEmailLiberacao

DEFAULT_CORPO = (
    "Prezados, favor liberar o acesso para a seguinte equipe:\n\n"
    "Empresa: {empresa}\n"
    "Solicitante: {solicitante}\n"
    "Período do Dia: {periodo}\n"
    "Datas Autorizadas: {datas}\n\n"
    "Técnicos Presentes:\n"
    "{tecnicos}"
)
DEFAULT_ASSINATURA = "Atenciosamente,\nSesenApp"


def _ensure_default_template():
    if PadraoEmailLiberacao.objects.exists():
        return

    PadraoEmailLiberacao.objects.create(
        nome="Template Padrão Liberação",
        assunto="[SEGURANÇA] Liberação de Acesso de Terceiros",
        corpo=DEFAULT_CORPO,
        assinatura=DEFAULT_ASSINATURA,
        ativo=True,
    )


@login_required
def configuracao_acessos(request):
    _ensure_default_template()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'save_email_template':
            template_id = request.POST.get('template_id')
            if template_id:
                template_obj = PadraoEmailLiberacao.objects.filter(id=template_id).first()
                if not template_obj:
                    template_obj = PadraoEmailLiberacao()
            else:
                template_obj = PadraoEmailLiberacao()

            email_destinatario = request.POST.get('email_destinatario', '').strip()
            if not email_destinatario:
                messages.error(request, 'Informe o e-mail destinatário da Segurança/Portaria.')
                return redirect('adm_setup:configuracao_acessos')

            template_obj.nome = request.POST.get('nome', template_obj.nome)
            template_obj.assunto = request.POST.get('assunto', template_obj.assunto)
            template_obj.email_destinatario = email_destinatario
            template_obj.email_copia = request.POST.get('email_copia', '').strip() or None
            template_obj.corpo = request.POST.get('corpo', template_obj.corpo)
            template_obj.assinatura = request.POST.get('assinatura', template_obj.assinatura)
            template_obj.ativo = request.POST.get('ativo') == 'on'
            template_obj.save()

            if template_obj.ativo:
                PadraoEmailLiberacao.objects.exclude(pk=template_obj.pk).update(ativo=False)
            elif not PadraoEmailLiberacao.objects.filter(ativo=True).exists():
                PadraoEmailLiberacao.objects.filter(pk=template_obj.pk).update(ativo=True)

            messages.success(request, 'Template salvo com sucesso!')
            return redirect('adm_setup:configuracao_acessos')

        elif action == 'delete_template':
            template_id = request.POST.get('template_id')
            if template_id:
                total = PadraoEmailLiberacao.objects.count()
                if total <= 1:
                    messages.error(request, 'Não é possível excluir o único template disponível.')
                    return redirect('adm_setup:configuracao_acessos')

                template_obj = PadraoEmailLiberacao.objects.filter(id=template_id).first()
                if template_obj:
                    era_ativo = template_obj.ativo
                    template_obj.delete()
                    if era_ativo:
                        proximo = PadraoEmailLiberacao.objects.order_by('-id').first()
                        if proximo:
                            proximo.ativo = True
                            proximo.save(update_fields=['ativo'])
                    messages.success(request, 'Template excluído com sucesso!')
            return redirect('adm_setup:configuracao_acessos')

    templates_email = PadraoEmailLiberacao.objects.all().order_by('-id')

    context = {
        'templates_email': templates_email,
    }
    return render(request, 'setups/configuracao_acessos.html', context)
