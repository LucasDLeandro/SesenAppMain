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
    pattern = r"(class " + viewset_name + r"\(.*?def )"
    # We want to insert the action at the very beginning of the class, or right after docstring
    # But it's easier to append before the `class ` of the NEXT class.
    match = re.search(r"class " + viewset_name + r"\(.*?:", content, re.DOTALL)
    if not match: return content
    start_idx = match.end()
    
    # find next class definition starting with "\nclass "
    next_class_match = re.search(r"\nclass ", content[start_idx:])
    if next_class_match:
        end_idx = start_idx + next_class_match.start()
    else:
        end_idx = len(content)
        
    class_body = content[start_idx:end_idx]
    if "def cancelar(" not in class_body:
        content = content[:end_idx] + cancelar_action + content[end_idx:]
    return content

content = add_action(content, "SolicitacaoAparelhoLinhaViewSet")
content = add_action(content, "SolicitacaoSenhaViewSet")
content = add_action(content, "NadaConstaViewSet")

with open(r'C:\Lucas\SesenAppMain\telefonia\views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Views patched!")
