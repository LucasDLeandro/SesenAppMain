from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template import loader
from ..models.mapa_servicos import Categoria, Servico
from ..forms.eng_reg_category_servi import CategoryForm, ServiceFormSet
from ..filters.cat_serv_filter import CatServFilter

def cat_serv_reg(request):
    template = 'ordens/cat_serv.html'
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        service_form = ServiceFormSet(request.POST)
        if category_form.is_valid() and service_form.is_valid():
            categoria = category_form.save()
            service_form.instance = categoria
            servicos = service_form.save()
            messages.success(request, f'Para a Categoria: {categoria.nome}, Foram criados: {len(servicos)} serviços criado com sucesso!')    
            return redirect('ordens:cat_serv_reg')
    else:
        category_form = CategoryForm()
        service_form = ServiceFormSet()
    return render(request, template, {'category_form': category_form, 'service_form': service_form})
        

def cat_serv_view(request):
    category_list = CatServFilter(request.GET, queryset=Categoria.objects.all())
    services_list = CatServFilter(request.GET, queryset=Servico.objects.all())
    category_form = CategoryForm()
    service_form = ServiceFormSet()

    

    if request.method == 'POST':
        print(request.method)
        category_form = CategoryForm(request.POST)
        service_form = ServiceFormSet(request.POST)
        if category_form.is_valid() and service_form.is_valid():
            categoria = category_form.save()
            service_form.instance = categoria
            servicos = service_form.save()
            messages.success(request, f'Para a Categoria: {categoria.nome_categoria}, Foram criados: {len(servicos)} serviços criado com sucesso!')    
            return redirect('ordens:cat_serv_list')
        else:
            print(f"Erros Categoria: {category_form.errors}")
            print(f"Erros Serviço: {service_form.errors}")

    context = {
        'category_form': category_form, 
        'service_form': service_form,
        'category_filter': category_list,
        'services_filter': services_list,
        'cat_list': category_list.qs,
        'serv_list': services_list.qs
    }
    template = 'ordens/cat_serv.html'
    
    return render(request, template, context)

   

