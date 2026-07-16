from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import UserSerializer

from django.contrib.auth.models import User, Group


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':

            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reenviar_email_boas_vindas(self, request, pk=None):
        user = self.get_object()
        
        # Gera e define a senha temporária padrão para o reenvio
        raw_password = 'Sesenapp123'
        user.set_password(raw_password)
        user.save()

        # Atualizar a flag do perfil
        from usuarios.models import Perfil
        perfil, _ = Perfil.objects.get_or_create(user=user)

        from adm_setup.models import ConfiguracaoGeral
        config = ConfiguracaoGeral.get_instance()

        if not config.notificar_novos_usuarios:
            return Response({'detail': 'Notificações estão desabilitadas nas configurações globais.'}, status=status.HTTP_400_BAD_REQUEST)

        email_destino = user.email
        if not email_destino:
            return Response({'detail': 'O usuário não possui um endereço de e-mail cadastrado.'}, status=status.HTTP_400_BAD_REQUEST)

        msg = config.mensagem_boas_vindas.format(
            usuario=user.username,
            senha=raw_password
        )

        try:
            from django.core.mail import send_mail
            send_mail(
                subject='Reenvio: Bem-vindo(a) ao Sistema',
                message=msg,
                from_email=None,
                recipient_list=[email_destino],
                fail_silently=False,
            )
            perfil.email_boas_vindas_enviado = True
            perfil.email_boas_vindas_erro = None
            perfil.save()
            return Response({'detail': 'E-mail reenviado com sucesso.'})
        except Exception as e:
            import traceback
            print("=== ERRO AO REENVIAR E-MAIL ===")
            traceback.print_exc()
            print("===============================")
            
            perfil.email_boas_vindas_enviado = False
            perfil.email_boas_vindas_erro = str(e)
            perfil.save()
            return Response({
                'detail': 'Falha ao reenviar e-mail.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)