from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
<<<<<<< HEAD
    path('base', views.base, name='base'),
=======
>>>>>>> ed281aa0ea4d6ae3766202da8af3391f48659dce
]