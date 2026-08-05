import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()
from django.test import Client
c = Client(HTTP_HOST='127.0.0.1')
from django.core.files.uploadedfile import SimpleUploadedFile
pdf = SimpleUploadedFile('test.pdf', b'fake pdf content', content_type='application/pdf')
r = c.post('/telefonia/api/solicitacoes/62/finalizar_administrativo/', {
    'termo_transferencia_interna': '2026/002610, 2026/002611, 2026/002612',
    'pdf_termos': [pdf, pdf, pdf]
})
if r.status_code == 500:
    import re
    match = re.search(r'(?<=<textarea id="traceback_area" cols="140" rows="25">)(.*?)(?=</textarea>)', r.content.decode('utf-8'), re.DOTALL)
    if match:
        with open('traceback.txt', 'w') as f:
            f.write(match.group(1))
    else:
        with open('traceback.txt', 'w') as f:
            f.write('No traceback found in HTML. Status 500')
else:
    with open('traceback.txt', 'w') as f:
        f.write(f'{r.status_code}\n{r.content}')
