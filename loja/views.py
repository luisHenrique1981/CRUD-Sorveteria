from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import ItemCarrinho, Produto


def home(request):
    # Pega o termo digitado na barra de pesquisa
    busca = request.GET.get('q', '').strip()
    # Pega o filtro de categoria se o usuário clicar nos botões de filtro
    categoria_filtro = request.GET.get('categoria', '').strip()

    # Começamos trazendo todos os produtos
    produtos = Produto.objects.all()

    # Se ele buscou por texto
    if busca:
        produtos = produtos.filter(nome__icontains=busca)
    
    # Se ele clicou em um botão de filtro de categoria
    if categoria_filtro:
        produtos = produtos.filter(categoria__iexact=categoria_filtro)

    # Se houver uma busca por texto ou por categoria ativa, 
    # redirecionamos para a nova página de listagem de ocorrências
    if busca or categoria_filtro:
        return render(request, 'loja/produto.html', {
            'produtos': produtos,
            'busca': busca,
            'categoria_atual': categoria_filtro
        })

    # Caso contrário, mostra a index.html normal com o cardápio completo
    return render(request, 'loja/index.html', {'produtos': produtos})

@login_required
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
            messages.error(request, "Não foi possível criar a conta. Por favor, corrija os erros destacados abaixo.")
            
    else:
        form = UserCreationForm()
        
    return render(request, 'loja/cadastro.html', {'form': form})

@login_required
def sobre(request):
    return render(request, 'loja/sobre.html')

@login_required
def contatos(request):
    return render(request, 'loja/contatos.html')


def pegar_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

@login_required
def produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    return render(request, 'loja/produto.html', {'produto': produto})

@login_required
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

@login_required
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

@login_required
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
    logout(request) 
    return redirect('home') 

@login_required
def finalizar_pedido(request):
    if not request.user.is_authenticated:
        return redirect('login')

    itens = ItemCarrinho.objects.filter(usuario=request.user)
    
    if itens.exists():
        itens.delete()
        messages.success(request, "Pedido finalizado com sucesso! Seu sorvete já está sendo preparado.")
    
    return redirect('carrinho')

@login_required
def aumentar_quantidade(request, item_id):
    session_key = pegar_session_key(request)
    
    if request.user.is_authenticated:
        item = get_object_or_404(ItemCarrinho, id=item_id, usuario=request.user)
    else:
        item = get_object_or_404(ItemCarrinho, id=item_id, session_key=session_key)
        
    item.quantidade += 1
    item.save()
    return redirect("carrinho")

@login_required
def diminuir_quantidade(request, item_id):
    session_key = pegar_session_key(request)
    
    if request.user.is_authenticated:
        item = get_object_or_404(ItemCarrinho, id=item_id, usuario=request.user)
    else:
        item = get_object_or_404(ItemCarrinho, id=item_id, session_key=session_key)
        
    if item.quantidade > 1:
        item.quantidade -= 1
        item.save()
    else:
        item.delete()
        
    return redirect("carrinho")