from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

# Imports dos models de cada app (usando try/except para evitar quebra caso algum app não esteja instalado ou model não exista)
try:
    from elevadores.models import ElevOrderReg
except ImportError:
    ElevOrderReg = None

try:
    from telefonia.models import TelefoneSolicitacao
except ImportError:
    TelefoneSolicitacao = None

try:
    from audiovideo.models import EventoAV
except ImportError:
    EventoAV = None

try:
    from reembolsos.models import SolicitacaoReembolso
except ImportError:
    SolicitacaoReembolso = None

@login_required
def hub_servicos_view(request):
    # Elevadores: Chamados Abertos
    elevadores_pendentes = 0
    if ElevOrderReg:
        try:
            elevadores_pendentes = ElevOrderReg.objects.filter(status__iexact='aberta').count()
        except Exception as e:
            logger.error(f"Erro ao buscar chamados de elevadores: {e}")
            
    # Telefonia: Solicitações Pendentes (não concluídas/não canceladas)
    telefonia_pendentes = 0
    if TelefoneSolicitacao:
        try:
            telefonia_pendentes = TelefoneSolicitacao.objects.exclude(status__iexact='concluida').exclude(status__iexact='cancelada').count()
        except Exception as e:
            logger.error(f"Erro ao buscar solicitações de telefonia: {e}")
            
    # Áudio e Vídeo: Eventos Futuros / Agendados
    audiovideo_pendentes = 0
    if EventoAV:
        try:
            # Excluíndo o que já foi finalizado
            audiovideo_pendentes = EventoAV.objects.exclude(status__iexact='concluido').exclude(status__iexact='cancelado').count()
        except Exception as e:
            logger.error(f"Erro ao buscar eventos de AV: {e}")
            
    # Reembolsos: Solicitações Pendentes
    reembolsos_pendentes = 0
    if SolicitacaoReembolso:
        try:
            reembolsos_pendentes = SolicitacaoReembolso.objects.filter(status__iexact='pendente').count()
        except Exception as e:
            logger.error(f"Erro ao buscar reembolsos: {e}")

    context = {
        'elevadores_pendentes': elevadores_pendentes,
        'telefonia_pendentes': telefonia_pendentes,
        'audiovideo_pendentes': audiovideo_pendentes,
        'reembolsos_pendentes': reembolsos_pendentes,
    }
    
    return render(request, 'hub_servicos.html', context)
