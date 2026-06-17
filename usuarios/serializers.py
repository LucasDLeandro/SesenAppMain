from django.contrib.auth.models import User, Group
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields= [
            'id',
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
        ]

        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
                'min_length': 8,
                'required': True
            },
            'email': {'required': True}
        }

        def validate_password(self, value):
            if value.isnumeric():
                raise serializers.ValidationError("A senha deve conter letras e números.")
            return value
        
        def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            return user