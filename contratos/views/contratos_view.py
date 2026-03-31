from django.shortcuts import render, redirect
from django.contrib import messages
from ..models.model_contratos import Contratos
from ..forms.form_contrato import Contrato

def contratoView(request):
    template = 'contratos/form_contratos.html'
    if request.method == 'POST':
        form_contratos = Contrato(request.POST)
        if form_contratos.is_valid():
            contrato = form_contratos.save()
            messages.success(request, f'O Contrato TSE nº {contrato.num_contrato}, foi registrado com sucesso.')
            return redirect('contratos:novo_contrato')
        else:
            for field, errors, in form_contratos.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no Campo {field}: {error}")
        
    else: 
        form_contratos = Contrato()
    context = {
        'form_contratos': form_contratos
    }
    return render(request, template, context)