from rest_framework import serializers
from .models import Empresa, ContatoEmpresa

from usuarios.models import Pessoa

class ContatoEmpresaSerializer(serializers.ModelSerializer):
    nome_contato = serializers.CharField(required=False, allow_blank=True)
    sobrenome = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    telefone = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ContatoEmpresa
        fields = ['id', 'empresa', 'pessoa', 'nome_contato', 'sobrenome', 'cargo', 'email', 'telefone', 'created_at', 'updated_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.pessoa:
            ret['nome_contato'] = instance.pessoa.nome
            ret['sobrenome'] = instance.pessoa.sobrenome or ''
            ret['email'] = instance.pessoa.email or ''
            ret['telefone'] = instance.pessoa.telefone or ''
        else:
            ret['nome_contato'] = 'Contato Sem Pessoa (Erro de Migração)'
            ret['sobrenome'] = ''
        return ret

    def create(self, validated_data):
        nome = validated_data.pop('nome_contato', '').strip()
        if not nome:
            raise serializers.ValidationError({"nome_contato": "O primeiro nome é obrigatório."})
            
        sobrenome = validated_data.pop('sobrenome', '')
        if sobrenome: sobrenome = sobrenome.strip()
        
        email = validated_data.pop('email', '')
        if email: email = email.strip()
        
        telefone = validated_data.pop('telefone', '')
        if telefone: telefone = telefone.strip()

        pessoa = None
        if email:
            pessoa = Pessoa.objects.filter(email=email).first()
        
        if pessoa:
            # Atualiza apenas campos vazios
            modificou = False
            if nome and not pessoa.nome: 
                pessoa.nome = nome
                modificou = True
            if sobrenome and not pessoa.sobrenome: 
                pessoa.sobrenome = sobrenome
                modificou = True
            if not pessoa.telefone and telefone: 
                pessoa.telefone = telefone
                modificou = True
            if modificou:
                pessoa.save()
        else:
            # Cria a pessoa
            pessoa = Pessoa.objects.create(
                nome=nome, 
                sobrenome=sobrenome, 
                email=email if email else None, 
                telefone=telefone
            )
        
        validated_data['pessoa'] = pessoa
        return super().create(validated_data)

    def update(self, instance, validated_data):
        import traceback
        try:
            nome = validated_data.pop('nome_contato', None)
            if nome is not None and not str(nome).strip():
                raise serializers.ValidationError({"nome_contato": "O primeiro nome é obrigatório."})
                
            sobrenome = validated_data.pop('sobrenome', None)
            email = validated_data.pop('email', None)
            telefone = validated_data.pop('telefone', None)

            pessoa = instance.pessoa
            if pessoa:
                if nome is not None: pessoa.nome = str(nome).strip()
                if sobrenome is not None: pessoa.sobrenome = str(sobrenome).strip()
                if email is not None: pessoa.email = str(email).strip() if email else None
                if telefone is not None: pessoa.telefone = str(telefone).strip()
                pessoa.save()
            elif nome:
                instance.pessoa = Pessoa.objects.create(
                    nome=str(nome).strip(), 
                    sobrenome=str(sobrenome).strip() if sobrenome else '', 
                    email=str(email).strip() if email else None, 
                    telefone=str(telefone).strip() if telefone else ''
                )

            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Erro interno: {str(e)}\n\n{traceback.format_exc()}"})

class EmpresaSerializer(serializers.ModelSerializer):
    contatos = ContatoEmpresaSerializer(many=True, read_only=True)

    class Meta:
        model = Empresa
        fields = '__all__'
