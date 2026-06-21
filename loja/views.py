from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ItemCarrinho


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

def pegar_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def adicionar_carrinho(request):
    if request.method == "POST":
        session_key = pegar_session_key(request)

        nome = request.POST.get("nome")
        categoria = request.POST.get("categoria")
        preco = request.POST.get("preco", "0")
        imagem = request.POST.get("imagem", "")
        quantidade = request.POST.get("quantidade", 1)

        preco = preco.replace("R$", "").replace("$", "").replace(",", ".").strip()

        try:
            preco = Decimal(preco)
        except InvalidOperation:
            preco = Decimal("0.00")

        try:
            quantidade = int(quantidade)
        except ValueError:
            quantidade = 1

        if request.user.is_authenticated:
            filtro = {
                "usuario": request.user,
                "nome": nome
            }
        else:
            filtro = {
                "session_key": session_key,
                "nome": nome
            }

        item = ItemCarrinho.objects.filter(**filtro).first()

        if item:
            item.quantidade += quantidade
            item.save()
        else:
            ItemCarrinho.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                nome=nome,
                categoria=categoria,
                preco=preco,
                quantidade=quantidade,
                imagem=imagem
            )

        messages.success(request, "Item adicionado ao carrinho!")
        return redirect("carrinho")

    return redirect("home")

def carrinho(request):
    session_key = pegar_session_key(request)

    if request.user.is_authenticated:
        itens = ItemCarrinho.objects.filter(usuario=request.user)
    else:
        itens = ItemCarrinho.objects.filter(session_key=session_key)

    total = sum(item.subtotal() for item in itens)

    return render(request, "loja/carrinho.html", {
        "itens": itens,
        "total": total
    })

def remover_item_carrinho(request, item_id):
    session_key = pegar_session_key(request)

    if request.user.is_authenticated:
        item = get_object_or_404(
            ItemCarrinho,
            id=item_id,
            usuario=request.user
        )
    else:
        item = get_object_or_404(
            ItemCarrinho,
            id=item_id,
            session_key=session_key
        )

    item.delete()
    messages.success(request, "Item removido do carrinho!")
    return redirect("carrinho")