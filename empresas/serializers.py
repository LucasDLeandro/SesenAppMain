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
        nome = validated_data.pop('nome_contato', '')
        sobrenome = validated_data.pop('sobrenome', '')
        email = validated_data.pop('email', None)
        telefone = validated_data.pop('telefone', None)

        pessoa = None
        if email:
            pessoa = Pessoa.objects.filter(email=email).first()
        
        if pessoa:
            if nome and not pessoa.nome: pessoa.nome = nome
            if sobrenome and not pessoa.sobrenome: pessoa.sobrenome = sobrenome
            if not pessoa.telefone and telefone: pessoa.telefone = telefone
            pessoa.save()
        else:
            if nome:
                pessoa = Pessoa.objects.create(
                    nome=nome, sobrenome=sobrenome, email=email, telefone=telefone
                )
        
        validated_data['pessoa'] = pessoa
        return super().create(validated_data)

    def update(self, instance, validated_data):
        nome = validated_data.pop('nome_contato', None)
        sobrenome = validated_data.pop('sobrenome', None)
        email = validated_data.pop('email', None)
        telefone = validated_data.pop('telefone', None)

        pessoa = instance.pessoa
        if pessoa:
            if nome is not None: pessoa.nome = nome
            if sobrenome is not None: pessoa.sobrenome = sobrenome
            if email is not None: pessoa.email = email
            if telefone is not None: pessoa.telefone = telefone
            pessoa.save()
        elif nome:
            instance.pessoa = Pessoa.objects.create(
                nome=nome, sobrenome=sobrenome, email=email, telefone=telefone
            )

        return super().update(instance, validated_data)

class EmpresaSerializer(serializers.ModelSerializer):
    contatos = ContatoEmpresaSerializer(many=True, read_only=True)

    class Meta:
        model = Empresa
        fields = '__all__'
