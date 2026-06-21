from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('base', views.base, name='base'),
    path('login', views.login, name='login'),
    path('cadastro', views.cadastro, name='cadastro'),
    path('sobre', views.sobre, name='sobre'),
    path('contatos', views.contatos, name='contatos'),
    path("carrinho/", views.carrinho, name="carrinho"),
    path("carrinho/adicionar/", views.adicionar_carrinho, name="adicionar_carrinho"),
    path("carrinho/remover/<int:item_id>/", views.remover_item_carrinho, name="remover_item_carrinho"),
    path('logout/', views.user_logout, name='logout'),
    path('finalizar-pedido/', views.finalizar_pedido, name='finalizar_pedido'),
]