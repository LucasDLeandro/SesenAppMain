from django.test import TestCase
from gestao_patrimonio.serializers import AparelhoVoipSerializer
from telefonia.models.aparelhos_telefonicos import AparelhoVoip

class AparelhoVoipSerializerTestCase(TestCase):
    def test_serializer_validation_funciona(self):
        data = {
            'patrimonio': '123456',
            'modelo': 'Yealink T21',
            'integridade': 'funciona',
            'status': 'estoque'
        }
        serializer = AparelhoVoipSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        aparelho = serializer.save()
        self.assertEqual(aparelho.integridade, 'funciona')

    def test_serializer_validation_defeito(self):
        data = {
            'patrimonio': '123457',
            'modelo': 'Yealink T21',
            'integridade': 'defeito',
            'status': 'estoque'
        }
        serializer = AparelhoVoipSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        aparelho = serializer.save()
        self.assertEqual(aparelho.integridade, 'defeito')
