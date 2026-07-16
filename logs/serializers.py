from rest_framework import serializers
from .models import SystemLog

class SystemLogSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField()
    modulo = serializers.SerializerMethodField()

    class Meta:
        model = SystemLog
        fields = ['id', 'usuario', 'action', 'modulo', 'object_id', 'timestamp', 'dados']

    def get_usuario(self, obj):
        if obj.user:
            return obj.user.first_name or obj.user.username
        return "Sistema"
        
    def get_modulo(self, obj):
        if obj.content_type:
            app_label = obj.content_type.app_label
            model_name = obj.content_type.model
            return f"{app_label.capitalize()} / {model_name.capitalize()}"
        return "Desconhecido"
