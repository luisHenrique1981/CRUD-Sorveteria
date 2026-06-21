from django.contrib import admin
from .models import ItemCarrinho, Produto

# Registra o carrinho do jeito que já estava
admin.site.register(ItemCarrinho)

# Registra o Produto com um painel customizado para a professora avaliar o CRUD
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco')
    list_filter = ('categoria',) # O filtro exigido pela professora!
    search_fields = ('nome',)    # Barra de pesquisa interna do painel admin