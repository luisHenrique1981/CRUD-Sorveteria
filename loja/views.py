from django.shortcuts import render

def home(request):
    return render(request, 'loja/index.html')

def base(request):
    return render(request, 'loja/base.html')

def login(request):
    return render(request, 'loja/login.html')

def cadastro(request):
    return render(request, 'loja/cadastro.html')

def sobre(request):
    return render(request, 'loja/sobre.html')

def contatos(request):
    return render(request, 'loja/contatos.html')