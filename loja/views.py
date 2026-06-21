from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import ItemCarrinho, Produto



def home(request):
    # 1. Pega a palavra que o usuário digitou na lupa
    busca = request.GET.get('q')

    # 2. Se a pessoa digitou algo, acionamos o filtro no Banco de Dados
    if busca:
        # O '__icontains' é mágico: ele ignora maiúsculas/minúsculas e acha partes da palavra.
        # Ex: se digitar "mora", ele acha "Sorvete de Morango".
        produtos = Produto.objects.filter(nome__icontains=busca)
    else:
        # Se a barra de pesquisa estiver vazia, carrega o cardápio inteiro
        produtos = Produto.objects.all()

    # 3. Envia os produtos (filtrados ou totais) para o template HTML desenhar
    return render(request, 'loja/index.html', {'produtos': produtos})

def base(request):
    return render(request, 'loja/base.html')

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'loja/login.html', {'form': form})

def cadastro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Eba! Conta criada com sucesso. Bem-vindo(a), {user.username}!")
            return redirect('home')
        else:
            # ATENÇÃO AQUI: Este 'else' precisa estar perfeitamente alinhado com o 'if form.is_valid():' acima dele!
            messages.error(request, "Não foi possível criar a conta. Por favor, corrija os erros destacados abaixo.")
            
    else:
        # ATENÇÃO AQUI: Este 'else' precisa estar alinhado com o 'if request.method == 'POST':'
        form = UserCreationForm()
        
    return render(request, 'loja/cadastro.html', {'form': form})
def sobre(request):
    return render(request, 'loja/sobre.html')

def contatos(request):
    return render(request, 'loja/contatos.html')

def pegar_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def adicionar_carrinho(request):
    if not request.user.is_authenticated:
        return redirect('login')
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
    if not request.user.is_authenticated:
        return redirect('login')

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
    if not request.user.is_authenticated:
        return redirect('login')
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

def user_logout(request):
    logout(request) # Encerra a sessão do usuário
    return redirect('home') # Joga ele de volta para a tela inicial

def finalizar_pedido(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Busca todos os itens do usuário atual e deleta do banco (esvazia o carrinho)
    itens = ItemCarrinho.objects.filter(usuario=request.user)
    
    if itens.exists():
        itens.delete()
        messages.success(request, "Pedido finalizado com sucesso! Seu sorvete já está sendo preparado.")
    
    return redirect('carrinho')