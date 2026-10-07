import re

with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

cancelar_action = """
    @action(detail=True, methods=['post'])
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
        return Response(serializer.data)
"""

def add_action(content, viewset_name):
    # Find the Viewset class
    idx = content.find(f"class {viewset_name}")
    if idx == -1: return content
    # Find the end of the class or the start of the next class
    next_class_idx = content.find("class ", idx + 10)
    if next_class_idx == -1:
        next_class_idx = len(content)
    
    if "def cancelar(" not in content[idx:next_class_idx]:
        # Insert before next class or at end
        content = content[:next_class_idx] + cancelar_action + "\n" + content[next_class_idx:]
    return content

content = add_action(content, "SolicitacaoAparelhoLinhaViewSet")
content = add_action(content, "SolicitacaoSenhaViewSet")
content = add_action(content, "NadaConstaViewSet")

with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Views patched!")
