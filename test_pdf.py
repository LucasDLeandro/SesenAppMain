import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()

import traceback
from telefonia.views import get_pdf_senha_bytes
from telefonia.models.solicitacao_senha import CriarSenha

for s in CriarSenha.objects.order_by('-id')[:3]:
    print(f"Testing ID {s.id}")
    try:
        bytes_pdf = get_pdf_senha_bytes(senha_id=s.id)
        if bytes_pdf:
            print(f"ID {s.id} OK, {len(bytes_pdf)} bytes")
        else:
            print(f"ID {s.id} returned None")
    except Exception as e:
        print(f"Exception on ID {s.id}:")
        traceback.print_exc()
