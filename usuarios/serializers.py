from django.contrib.auth.models import User, Group
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    telefone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    perfil_telefone = serializers.SerializerMethodField(read_only=True)
    email_boas_vindas_enviado = serializers.SerializerMethodField(read_only=True)
    email_boas_vindas_erro = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields= [
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'telefone',
            'perfil_telefone',
            'email_boas_vindas_enviado',
            'email_boas_vindas_erro'
        ]

        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
                'min_length': 6,
                'required': False
            },
            'email': {'required': True, 'allow_blank': False}
        }

    def get_perfil_telefone(self, obj):
        try:
            if obj.perfil and obj.perfil.telefone:
                return obj.perfil.telefone
        except Exception:
            pass
        return ''

    def get_email_boas_vindas_enviado(self, obj):
        try:
            if obj.perfil:
                return obj.perfil.email_boas_vindas_enviado
        except Exception:
            pass
        return False

    def get_email_boas_vindas_erro(self, obj):
        try:
            if obj.perfil:
                return obj.perfil.email_boas_vindas_erro
        except Exception:
            pass
        return None

    def validate_password(self, value):
        if value.isnumeric():
            raise serializers.ValidationError("A senha deve conter letras e números.")
        return value

    def validate_telefone(self, value):
        if value:
            import re
            value = re.sub(r'\D', '', value)
            if len(value) in (10, 11) and not value.startswith('55'):
                value = f"55{value}"
        return value
    
    def create(self, validated_data):
        telefone = validated_data.pop('telefone', None)
        raw_password = validated_data.get('password', '<Senha Oculta>')
        user = User.objects.create_user(**validated_data)
        
        from usuarios.models import Perfil
        perfil, created = Perfil.objects.get_or_create(user=user)
        if telefone:
            perfil.telefone = telefone
            perfil.save()
            
        # Notifica o novo usuário por e-mail
        from adm_setup.models import ConfiguracaoGeral
        config = ConfiguracaoGeral.get_instance()
        if config.notificar_novos_usuarios:
            try:
                email_destino = user.email
                if email_destino:
                    msg = config.mensagem_boas_vindas.format(
                        usuario=user.username,
                        senha=raw_password
                    )
                    from django.core.mail import send_mail
                    # Usamos fail_silently=False para capturar o erro exato
                    send_mail(
                        subject='Bem-vindo(a) ao Sistema',
                        message=msg,
                        from_email=None,
                        recipient_list=[email_destino],
                        fail_silently=False,
                    )
                    perfil.email_boas_vindas_enviado = True
                    perfil.email_boas_vindas_erro = None
                    perfil.save()
            except Exception as e:
                print(f"Erro ao disparar E-mail de boas vindas (API): {e}")
                perfil.email_boas_vindas_erro = str(e)
                perfil.save()
                
        return user

    def update(self, instance, validated_data):
        telefone = validated_data.pop('telefone', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        
        from usuarios.models import Perfil
        perfil, created = Perfil.objects.get_or_create(user=instance)
        if telefone is not None:
            perfil.telefone = telefone
            perfil.save()
            
        return instance