import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()

from contratos.models.model_contratos import Profissional
from empresas.models import ContatoEmpresa
from usuarios.models import Pessoa

def run_migration():
    print("Migrating Profissionais...")
    for p in Profissional.objects.all():
        if not p.pessoa:
            if p.cpf:
                pessoa, created = Pessoa.objects.get_or_create(
                    cpf=p.cpf,
                    defaults={
                        'nome': p.nome,
                        'email': p.email,
                        'telefone': p.telefone
                    }
                )
            else:
                pessoa = Pessoa.objects.create(
                    nome=p.nome,
                    email=p.email,
                    telefone=p.telefone
                )
                created = True
                
            if not created:
                if not pessoa.email and p.email: pessoa.email = p.email
                if not pessoa.telefone and p.telefone: pessoa.telefone = p.telefone
                pessoa.save()
            p.pessoa = pessoa
            p.save()

    print("Migrating Contatos...")
    for c in ContatoEmpresa.objects.all():
        if not c.pessoa:
            if c.email:
                pessoa, created = Pessoa.objects.get_or_create(
                    email=c.email,
                    defaults={'nome': c.nome_contato, 'telefone': c.telefone}
                )
            else:
                pessoa = Pessoa.objects.create(
                    nome=c.nome_contato,
                    telefone=c.telefone
                )
                created = True
            c.pessoa = pessoa
            c.save()

    print("Done!")

if __name__ == '__main__':
    run_migration()
