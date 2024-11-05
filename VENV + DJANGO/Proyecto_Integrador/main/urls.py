

from django.urls import path
from main.views import *

from django.urls import path
from . import views


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('reserva/', ReservaView.as_view(), name='reserva'),
    path('contacto/', ContactoView.as_view(), name='contacto'),
    path('misreservas/', MisReservasView.as_view(), name='misreservas'),
    path('cliente/success/', CustomRegisterView.as_view(template_name='cliente_success.html'), name='cliente_success'),
    path('login/', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('register/', CustomRegisterView.as_view(), name='registrar'),
    path('mi-reserva/<int:reserva_id>/', mi_reserva.as_view(), name='mi_reserva'),
    path('misreservas/cancelar/<int:pk>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('jugadores/<int:partida_id>/<int:reserva_id>/', JugadoresView.as_view(), name='jugadores'),
    path('nombres-jugadores/<int:partida_id>/<int:reserva_id>/', NombresJugadoresView.as_view(), name='nombres_jugadores'),
    path('iniciar_partida/<int:partida_id>/', views.iniciar_partida, name='iniciar_partida'),
    path('tabla-partida/<int:partida_id>/', TablaView.as_view(), name='tabla'),
    path('mi-reserva/<int:reserva_id>/agregar_pedido/', AgregarPedidoView.as_view(), name='agregar_pedido'),
    path('finalizar-reserva/<int:reserva_id>/', views.finalizar_reserva, name='finalizar_reserva'),
    path('ver-reservas/', VerReservasView.as_view(), name='ver_reservas'),
    path('ver-reservas/', VerReservasView.as_view(), name='ver_reservas'),
    path('editar-reserva/<int:pk>/', EditarReservaView.as_view(), name='editar_reserva'),
    path('ver_pedidos/', VerPedidosView.as_view(), name='ver_pedidos'),
    path('editar_pedido/<int:pk>/', EditarPedidoView.as_view(), name='editar_pedido'),
    path('eliminar_pedido/<int:pk>/', EliminarPedidoView.as_view(), name='cancelar_pedido'),
    path('ver_pistas/', VerPistasView.as_view(), name='ver_pistas'),
    path('editar_pista/<int:pk>/', EditarPistaView.as_view(), name='editar_pista')
]
