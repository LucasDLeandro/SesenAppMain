from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import SystemLog
from .middleware import get_current_user
import datetime
from django.db.models.fields.files import FieldFile

def get_instance_data(instance):
    data = {}
    try:
        from decimal import Decimal
        for field in instance._meta.fields:
            value = getattr(instance, field.name, None)
            if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                value = str(value)
            elif isinstance(value, FieldFile):
                value = value.name if value else None
            elif isinstance(value, Decimal):
                value = float(value)
            elif hasattr(value, 'pk'):
                value = str(value.pk)
            data[field.name] = value
    except Exception:
        pass
    return data

# List of apps to audit
APPS_TO_AUDIT = ['telefonia', 'elevadores', 'audiovideo', 'reembolsos', 'clientes', 'notificacoes']

@receiver(post_save)
def audit_log_save(sender, instance, created, **kwargs):
    # Ignore models not in our apps, and ignore the SystemLog model itself
    if sender._meta.app_label in APPS_TO_AUDIT and sender._meta.model_name != 'systemlog':
        user = get_current_user()
        action = 'CREATE' if created else 'UPDATE'
        # Convert PK to string
        obj_id = str(instance.pk)
        SystemLog.objects.create(
            user=user,
            action=action,
            content_object=instance,
            object_id=obj_id,
            dados=get_instance_data(instance)
        )

@receiver(pre_delete)
def audit_log_delete(sender, instance, **kwargs):
    if sender._meta.app_label in APPS_TO_AUDIT and sender._meta.model_name != 'systemlog':
        user = get_current_user()
        obj_id = str(instance.pk)
        
        # We can't use GenericForeignKey because the object is deleted.
        # But we can store the content_type and object_id directly.
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(instance)
        
        SystemLog.objects.create(
            user=user,
            action='DELETE',
            content_type=ct,
            object_id=obj_id,
            dados=get_instance_data(instance)
        )
