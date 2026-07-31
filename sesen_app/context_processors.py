from elevadores.models import ElevOrderReg
from telefonia.models import TelefoneSolicitacao, CriarSenha, EmprestimoEvento
from reembolsos.models import SolicitacaoReembolso
from audiovideo.models import EventoAV, OrdemServicoAV

def pendencias_count(request):
    counts = {
        'pendencias_elevadores': 0,
        'pendencias_telefonia': 0,
        'pendencias_reembolsos': 0,
        'pendencias_audiovideo': 0,
    }

    if request.user.is_authenticated:
        try:
            counts['pendencias_elevadores'] = ElevOrderReg.objects.exclude(status__in=['CONCLUIDA', 'CANCELADA']).count()
        except Exception:
            pass

        try:
            solic_aparelho = TelefoneSolicitacao.objects.exclude(status='concluida').count()
            solic_senha = CriarSenha.objects.exclude(status='finalizada').count()
            emp_evento = EmprestimoEvento.objects.filter(status='em_andamento').count()
            counts['pendencias_telefonia'] = solic_aparelho + solic_senha + emp_evento
        except Exception:
            pass

        try:
            counts['pendencias_reembolsos'] = SolicitacaoReembolso.objects.exclude(status__in=['concluido', 'negada']).count()
        except Exception:
            pass

        try:
            eventos_av = EventoAV.objects.exclude(status__in=['concluido', 'cancelado']).count()
            os_av = OrdemServicoAV.objects.exclude(status__in=['concluida', 'cancelada']).count()
            counts['pendencias_audiovideo'] = eventos_av + os_av
        except Exception:
            pass

    return counts
