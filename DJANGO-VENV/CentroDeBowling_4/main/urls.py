

from django.urls import path
from django.contrib import admin
from main.views import IndexView, ClienteCreateView, ClienteListView, CustomLoginView, custom_logout_view




urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('cliente/add/', ClienteCreateView.as_view(), name='cliente_add'),
    path('cliente/success/', ClienteCreateView.as_view(template_name='cliente_success.html'), name='cliente_success'),
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('login/', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    
    
]
