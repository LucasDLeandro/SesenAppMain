from rest_framework import viewsets
from .models import SystemLog
from .serializers import SystemLogSerializer
from .permissions import IsAdminPerfil

class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Apenas visualização dos logs para Administradores.
    """
    queryset = SystemLog.objects.all().order_by('-timestamp')
    serializer_class = SystemLogSerializer
    permission_classes = [IsAdminPerfil]
