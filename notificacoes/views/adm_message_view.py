from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from notificacoes.models.template_notificacao import TemplateMessage