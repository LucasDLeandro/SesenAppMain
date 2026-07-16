# Generated manually to remove unique constraints from protocolo and autorizacao_sad fields
# This allows multiple solicitacoes to share the same protocolo and autorizacao_sad values

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telefonia', '0012_rename_avaliacao_telefonesolicitacao_relatorio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telefonesolicitacao',
            name='protocolo',
            field=models.CharField(
                editable=True,
                help_text='Protocolo SEI do Documento',
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='telefonesolicitacao',
            name='autorizacao_sad',
            field=models.CharField(
                editable=True,
                help_text='Protocolo SEI do Documento que autoriza a instalação',
                max_length=20,
                null=True,
            ),
        ),
    ]
