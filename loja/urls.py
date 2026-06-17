from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('base', views.base, name='base'),
    path('login', views.login, name='login'),
    path('cadastro', views.cadastro, name='cadastro'),
]