from django.contrib import admin
from .models import Cliente, PistaBowling, Reserva, EstadoReserva, Jugador, Partida, EstadoPartida, Turno, Tirada, EstadoPista, Pedido, EstadoPedido, PedidoXProducto, Producto, HistorialEstado


admin.site.register(Cliente)
admin.site.register(PistaBowling)
admin.site.register(Reserva)
admin.site.register(EstadoReserva)
admin.site.register(Jugador)
admin.site.register(Partida)
admin.site.register(EstadoPartida)
admin.site.register(Turno)
admin.site.register(Tirada)
admin.site.register(EstadoPista)
admin.site.register(Pedido)
admin.site.register(EstadoPedido)
admin.site.register(PedidoXProducto)
admin.site.register(Producto)
admin.site.register(HistorialEstado)

