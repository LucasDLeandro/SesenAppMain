from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

def main_ordens(request):
    return render(request, 'ordens/base_ordens.html')