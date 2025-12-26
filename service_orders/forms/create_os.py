from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from ..models.reg_os_model import ServiceOrder

class CreateOsForm(ModelForm):
    class Meta:
        model = ServiceOrder
        fields = [
            'data_hora',
            'protocolo',
            'elevador',
            'aprisionamento',
            'ocorrencia',
            'atendente',
            'solicitante',
            'elevador_parado',
            ]
        
        labels = {
            'data_hora': 'Data e Hora',
            'protocolo': 'Protocolo',
            'elevador': 'Eelevador',
            'aprisionamento': 'Elevador parou, causando aprisionamento?'
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'register-os-form'
        self.helper.form_class='row g-3'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        self.helper.add_input(Submit('submit', 'Create Service Order'))
