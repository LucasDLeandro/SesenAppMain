import re

with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the cancelar method in CriarSenhaViewSet
old_cancelar = """    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        solicitacao = self.get_object()
        from django.utils import timezone
        justificativa = request.data.get('justificativa', '').strip()
        if not justificativa:
            return Response({'error': 'Justificativa é obrigatória para cancelar.'}, status=400)
        
        solicitacao.status = 'cancelada'
        solicitacao.justificativa_cancelamento = justificativa
        solicitacao.cancelado_por = request.user.get_full_name() or request.user.username
        solicitacao.data_cancelamento = timezone.now()
        solicitacao.save(update_fields=['status', 'justificativa_cancelamento', 'cancelado_por', 'data_cancelamento'])
        
        serializer = self.get_serializer(solicitacao)
        return Response(serializer.data)"""

new_cancelar = """    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        try:
            solicitacao = self.get_object()
            from django.utils import timezone
            justificativa = request.data.get('justificativa', '').strip()
            if not justificativa:
                return Response({'error': 'Justificativa é obrigatória para cancelar.'}, status=400)
            
            solicitacao.status = 'cancelada'
            solicitacao.justificativa_cancelamento = justificativa
            solicitacao.cancelado_por = request.user.get_full_name() or request.user.username
            solicitacao.data_cancelamento = timezone.now()
            solicitacao.save(update_fields=['status', 'justificativa_cancelamento', 'cancelado_por', 'data_cancelamento'])
            
            serializer = self.get_serializer(solicitacao)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            return Response({'error': str(e), 'traceback': traceback.format_exc()}, status=500)"""

content = content.replace(old_cancelar, new_cancelar)

with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Debug patch applied!")
