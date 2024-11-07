#_____________________________________________________
#_____________ IMPORTS__________________________________
#_____________________________________________________



from django.shortcuts import render



from django.views.generic import TemplateView,DeleteView
from django.urls import reverse_lazy

from .forms import  CustomLoginForm
from django.views.generic import ListView
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse
from datetime import datetime, timedelta


from django.shortcuts import render, redirect
from .forms import ReservaForm

from django.views.generic import CreateView
import logging

from django.http import JsonResponse


from django.shortcuts import render

from django.views.generic import View
from django.shortcuts import render, redirect
from .forms import JugadoresForm
from .models import Partida
from .models import Pedido, PedidoXProducto, EstadoPedido, Producto

from django.views.generic import View
from django.shortcuts import render, redirect
from .models import Partida, Jugador

from django.shortcuts import render, redirect
from django.views.generic import View
from .models import Partida, Jugador, Reserva

from django.shortcuts import get_object_or_404

from django.views.generic import ListView
from .models import Reserva, HistorialEstado


from django.shortcuts import redirect

from django.utils import timezone
from datetime import timedelta

from django.http import JsonResponse, HttpRequest

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from .models import Partida, Jugador, Tirada, Turno

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from .models import Partida, Jugador, Tirada, Turno

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from .models import Partida, Jugador, Tirada, Turno, EstadoPartida

from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Reserva, EstadoReserva, HistorialEstado
from .forms import ReservaEditForm
from django.contrib import messages
from django.utils import timezone

from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import Reserva, HistorialEstado


from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomRegisterForm

from django.views.generic import TemplateView   

from .models import Reserva, Pedido, PedidoXProducto, Producto, HistorialEstado, Partida, EstadoPartida, Jugador

from django.views.generic import TemplateView

from .models import Reserva, Pedido, PedidoXProducto, Producto, HistorialEstado, Partida, EstadoPartida, Jugador

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from .models import Reserva, Pedido, PedidoXProducto, Producto, HistorialEstado, Partida, EstadoPartida, Jugador

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from .models import Reserva, Pedido, PedidoXProducto, Producto, HistorialEstado, Partida, EstadoPartida, Jugador, EstadoReserva

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from .models import Reserva, Pedido, PedidoXProducto, Producto, HistorialEstado, Partida, EstadoPartida, Jugador, EstadoReserva



from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Partida, Jugador, Turno, EstadoPartida


from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Reserva, Pedido, PedidoXProducto, Producto

from django.utils import timezone

from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Reserva, Pedido, PedidoXProducto, Producto, EstadoPedido

from django.utils import timezone

from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Reserva, Pedido, PedidoXProducto, EstadoPedido
from .forms import MultiplePedidoForm
from django.utils import timezone


from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseNotFound
from .models import Reserva, Pedido, PedidoXProducto, Producto, HistorialEstado, Partida, EstadoPartida, Jugador

#_____________________________________________________
#_____________ VIEWS__________________________________
#_____________________________________________________

class IndexView(TemplateView):
    template_name = 'index.html'

class MisReservasView(ListView): #modularizada
    model = Reserva
    template_name = 'misreservas.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        reservas = Reserva.objects.filter(id_cliente=self.request.user.id_cliente)
        ahora = timezone.now()

        for reserva in reservas:
            self._procesar_reserva(reserva, ahora)

        return reservas

    def _procesar_reserva(self, reserva, ahora):
        self._actualizar_ultimo_estado(reserva)
        self._verificar_confirmacion(reserva, ahora)
        self._verificar_estado_actual(reserva, ahora)
        self._verificar_finalizacion(reserva, ahora)
        self._actualizar_fecha_hora_fin(reserva)

    def _actualizar_ultimo_estado(self, reserva):
        
        try:
            reserva.ultimo_estado = reserva.historialestado_set.latest('fecha_hora_inicio')
        except HistorialEstado.DoesNotExist:
            reserva.ultimo_estado = None

    def _verificar_confirmacion(self, reserva, ahora):
        estado_default = EstadoReserva.objects.get(estado='Confirmada')
        if not HistorialEstado.objects.filter(id_reserva=reserva, estado=estado_default).exists():
            self._crear_historial_estado(reserva, estado_default, ahora, ahora + timedelta(hours=2))

    def _verificar_estado_actual(self, reserva, ahora):
        if reserva.fecha_hora_reserva and reserva.fecha_hora_reserva <= ahora:
            estado_en_curso = EstadoReserva.objects.get(estado='En Curso')
            if reserva.ultimo_estado.estado.estado == 'Confirmada':
                self._crear_historial_estado(reserva, estado_en_curso, ahora, ahora + timedelta(hours=2))

    def _verificar_finalizacion(self, reserva, ahora):
        if reserva.fecha_hora_fin and reserva.fecha_hora_reserva <= ahora and reserva.fecha_hora_fin <= ahora.time():
            estado_finalizada = EstadoReserva.objects.get(estado='Finalizada')
            if reserva.ultimo_estado.estado.estado == 'En Curso':
                self._crear_historial_estado(reserva, estado_finalizada, ahora, ahora)

    def _actualizar_fecha_hora_fin(self, reserva):
        if reserva.fecha_hora_reserva:
            hora_final = reserva.fecha_hora_reserva + timedelta(hours=2)
            reserva.fecha_hora_fin = hora_final.time()
            reserva.save()

    def _crear_historial_estado(self, reserva, estado, fecha_inicio, fecha_fin):
        if HistorialEstado.objects.filter(id_reserva = reserva, estado = estado).exists():
            HistorialEstado.objects.filter(id_reserva = reserva, estado = estado).delete()
        HistorialEstado.objects.create(
            id_reserva=reserva,
            estado=estado,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin
        )

def cancelar_reserva(request, pk):
        reserva = Reserva.objects.get(pk=pk)
        reserva.delete()
        return redirect('misreservas')

class ContactoView(TemplateView): #modularizada
    template_name = 'contacto.html'


class mi_reserva(TemplateView): #mod
    template_name = 'menu_partidas_bar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reserva_id = self.kwargs['reserva_id']

        try:
            reserva = self.get_reserva(reserva_id)
            pedidos = self.get_pedidos(reserva)
            estado_reserva = self.get_estado_reserva(reserva)
            partidas = self.get_or_create_partidas(reserva)
            self.update_partidas_status(partidas, estado_reserva)
            total_a_pagar = self.calculate_total_to_pay(pedidos)

            context.update({
                'reserva': reserva,
                'partidas': partidas,
                'pedidos': pedidos,
                'totalAPagar': total_a_pagar,
                'estado_reserva': estado_reserva,
                'productos': self.get_all_products()
            })
        except Reserva.DoesNotExist:
            context.update(self.get_empty_context())
        
        return context

    def get_reserva(self, reserva_id):
        return get_object_or_404(Reserva, pk=reserva_id, id_cliente=self.request.user.id_cliente)

    def get_pedidos(self, reserva):
        return Pedido.objects.filter(id_reserva=reserva.id_reserva)

    def get_estado_reserva(self, reserva):
        try:
            ultimo_estado = reserva.historialestado_set.latest('fecha_hora_inicio')
            return ultimo_estado.estado.estado
        except HistorialEstado.DoesNotExist:
            return 'Confirmada'

    def get_or_create_partidas(self, reserva):
        partidas = list(Partida.objects.filter(id_reserva=reserva).order_by('id_partida'))
        if len(partidas) < 3:
            self.create_missing_partidas(reserva, partidas)
        return partidas

    def create_missing_partidas(self, reserva, partidas):
        estado_bloqueado = EstadoPartida.objects.get(estado='Bloqueada')
        for _ in range(3 - len(partidas)):
            nueva_partida = Partida.objects.create(
                id_pista=reserva.id_pista,
                id_reserva=reserva,
                estado=estado_bloqueado,
                cant_jugadores=0
            )
            partidas.append(nueva_partida)

    def update_partidas_status(self, partidas, estado_reserva):
        estado_disponible = EstadoPartida.objects.get(estado='Disponible')
        estado_bloqueado = EstadoPartida.objects.get(estado='Bloqueada')
        estado_en_proceso = EstadoPartida.objects.get(estado='En proceso')
        estado_finalizado = EstadoPartida.objects.get(estado='Finalizada')

        for i, partida in enumerate(partidas):
            self.update_partida_status(partida, i, partidas, estado_reserva, estado_disponible, estado_bloqueado, estado_en_proceso, estado_finalizado)

    def update_partida_status(self, partida, index, partidas, estado_reserva, estado_disponible, estado_bloqueado, estado_en_proceso, estado_finalizado):
        if estado_reserva == 'En curso':
            self.update_partida_status_en_curso(partida, index, partidas, estado_disponible, estado_bloqueado, estado_finalizado, estado_en_proceso)
        else:
            self.update_partida_status_not_en_curso(partida, estado_bloqueado, estado_finalizado, estado_en_proceso)

        if partida.estado == estado_finalizado:
            self.set_partida_winner(partida)

        partida.save()

    def update_partida_status_en_curso(self, partida, index, partidas, estado_disponible, estado_bloqueado, estado_finalizado, estado_en_proceso):
        if index == 0 and partida.estado not in [estado_finalizado, estado_en_proceso]:
            partida.estado = estado_disponible
        elif index > 0 and partidas[index-1].estado == estado_finalizado and partida.estado not in [estado_finalizado, estado_en_proceso]:
            partida.estado = estado_disponible
        elif partida.estado not in [estado_finalizado, estado_en_proceso]:
            partida.estado = estado_bloqueado

    def update_partida_status_not_en_curso(self, partida, estado_bloqueado, estado_finalizado, estado_en_proceso):
        if partida.estado not in [estado_finalizado, estado_en_proceso]:
            partida.estado = estado_bloqueado

    def set_partida_winner(self, partida):
        jugadores = Jugador.objects.filter(id_partida=partida)
        if jugadores.exists():
            puntajes = self.calculate_player_scores(jugadores)
            ganador = max(puntajes, key=puntajes.get)
            partida.ganador = ganador

    def calculate_player_scores(self, jugadores):
        return {jugador: sum(tirada.pinos_deribados for tirada in jugador.tirada_set.all()) for jugador in jugadores}

    def calculate_total_to_pay(self, pedidos):
        return sum(
            item.cantidad * item.id_producto.precio
            for pedido in pedidos
            for item in pedido.pedidoxproducto_set.all()
        )

    def get_all_products(self):
        return Producto.objects.all()

    def get_empty_context(self):
        return {
            'reserva': None,
            'pedidos': None,
            'partidas': [],
            'estado_reserva': None
        }

    def post(self, request, *args, **kwargs):
        reserva_id = self.kwargs['reserva_id']
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))

        try:
            reserva = self.get_reserva(reserva_id)
            producto = self.get_producto(producto_id)
            pedido = self.get_or_create_pedido(reserva)
            self.update_or_create_pedido_producto(pedido, producto, cantidad)
            return redirect('mi_reserva', reserva_id=reserva_id)
        except Reserva.DoesNotExist:
            return HttpResponseNotFound("Reserva no encontrada")

    def get_producto(self, producto_id):
        return get_object_or_404(Producto, pk=producto_id)

    def get_or_create_pedido(self, reserva):
        pedido, _ = Pedido.objects.get_or_create(id_reserva=reserva)
        return pedido

    def update_or_create_pedido_producto(self, pedido, producto, cantidad):
        pedido_producto, created = self.get_or_create_pedido_producto(pedido, producto)
        if created:
            pedido_producto.cantidad = cantidad
        else:
            pedido_producto.cantidad += cantidad
        pedido_producto.save()

    def get_or_create_pedido_producto(self, pedido, producto):
        return PedidoXProducto.objects.get_or_create(
            id_pedido=pedido,
            id_producto=producto,
            defaults={'cantidad': 0}
        )
class TablaView(TemplateView):#MOD
    template_name = 'tabla.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partida_id = self.kwargs['partida_id']
        partida = self.get_partida(partida_id)
        
        jugadores = self.get_jugadores(partida)
        turnos = self.get_turnos(partida)
        tiradas = self.get_tiradas(turnos)
        
        tiradas_dict, puntaje_jugador = self.process_tiradas(jugadores, tiradas)
        current_turn = self.get_current_turn(partida)

        context.update({
            'reserva': partida.id_reserva,
            'partida': partida,
            'jugadores': jugadores,
            'turnos': turnos,
            'num_partida': partida_id,
            'tiradas': tiradas,
            'tiradas_dict': tiradas_dict,
            'puntaje_jugador': puntaje_jugador,
            'current_turn': current_turn,
        })

        return context

    def post(self, request, partida_id):
        partida = self.get_partida(partida_id)
        jugadores = self.get_jugadores(partida)
        current_turn = self.get_current_turn(partida)
        hay_error = False

        for jugador in jugadores:
            if not self.jugador_tiene_datos(request, jugador, current_turn):
                continue

            tiradas_jugador, hay_error = self.process_jugador_tiradas(request, jugador, current_turn)
            
            if hay_error:
                self.delete_tiradas(tiradas_jugador)
                messages.error(request, f"⦁ Todas las tiradas deben ser registradas por el jugador {jugador.nombre_jugador} en el turno {current_turn.orden}.")

        if not hay_error and self.is_game_finished(partida):
            self.finalize_game(partida)
            return redirect('mi_reserva', reserva_id=partida.id_reserva.id_reserva)

        return redirect('tabla', partida_id=partida_id)

    def get_partida(self, partida_id):
        return get_object_or_404(Partida, id_partida=partida_id)

    def get_jugadores(self, partida):
        return Jugador.objects.filter(id_partida=partida)

    def get_turnos(self, partida):
        return Turno.objects.filter(id_partida=partida).order_by('numero_turno')

    def get_tiradas(self, turnos):
        return Tirada.objects.filter(numero_turno__in=turnos)

    def process_tiradas(self, jugadores, tiradas):
        tiradas_dict = {}
        puntaje_jugador = {jugador.id_jugador: 0 for jugador in jugadores}
        for tirada in tiradas:
            key = f"{tirada.id_jugador.id_jugador}-{tirada.numero_turno.numero_turno}"
            if key not in tiradas_dict:
                tiradas_dict[key] = []
            tiradas_dict[key].append(tirada)
            puntaje_jugador[tirada.id_jugador.id_jugador] += tirada.pinos_deribados
        return tiradas_dict, puntaje_jugador

    def jugador_tiene_datos(self, request, jugador, current_turn):
        return any(
            request.POST.get(f'jugador_{jugador.id_jugador}_turno_{current_turn.numero_turno}_tirada_{j}', '')
            for j in range(1, 4 if current_turn.ultimo_turno else 3)
        )

    def process_jugador_tiradas(self, request, jugador, current_turn):
        tiradas_range = range(1, 4) if current_turn.ultimo_turno else range(1, 3)
        primera_tirada = None
        tiradas_jugador = []
        hay_error = False

        for j in tiradas_range:
            clave = f'jugador_{jugador.id_jugador}_turno_{current_turn.numero_turno}_tirada_{j}'
            pinos_derribados = request.POST.get(clave, '')

            if self.is_valid_tirada(pinos_derribados, current_turn, primera_tirada):
                pinos_derribados = int(pinos_derribados) if pinos_derribados.isdigit() else 0
                tirada = self.create_tirada(jugador, current_turn, j, pinos_derribados)
                tiradas_jugador.append(tirada)
                if j == 1:
                    primera_tirada = tirada
            else:
                hay_error = True
                self.add_error_message(request, jugador, current_turn, j, pinos_derribados)
                break

        return tiradas_jugador, hay_error

    def is_valid_tirada(self, pinos_derribados, current_turn, primera_tirada):
        if current_turn.ultimo_turno:
            return True
        if pinos_derribados.isdigit():
            pinos_derribados = int(pinos_derribados)
            max_pinos = 10 - (primera_tirada.pinos_deribados if primera_tirada else 0)
            return 0 <= pinos_derribados <= max_pinos
        return False

    def create_tirada(self, jugador, current_turn, orden, pinos_derribados):
        return Tirada.objects.create(
            pinos_deribados=int(pinos_derribados),
            orden=orden,
            id_jugador=jugador,
            numero_turno=current_turn,
        )

    def add_error_message(self, request, jugador, current_turn, j, pinos_derribados):
        if pinos_derribados == '':
            messages.error(request, f"⦁ Turno {current_turn.orden} invalido para el jugador {jugador.nombre_jugador}, tirada {j}: El campo no puede estar vacío.")
        elif not current_turn.ultimo_turno:
            messages.error(request, f"⦁ Turno {current_turn.orden} invalido para el jugador {jugador.nombre_jugador}, tirada {j}: Es imposible tirar mas de 10 pinos.")
        else:
            messages.error(request, f"⦁ Turno {current_turn.orden} invalido para el jugador {jugador.nombre_jugador}, tirada {j}: Debe ser un numero.")

    def delete_tiradas(self, tiradas):
        for tirada in tiradas:
            tirada.delete()

    def get_current_turn(self, partida):
        turnos = self.get_turnos(partida)
        tiradas = self.get_tiradas(turnos)
        tiradas_count = tiradas.count()
        jugadores_count = self.get_jugadores(partida).count()
        
        current_turn_index = tiradas_count // (2 * jugadores_count)
        if current_turn_index < len(turnos):
            return turnos[current_turn_index]
        else:
            return turnos.last()

    def is_game_finished(self, partida):
        turnos = self.get_turnos(partida)
        jugadores = self.get_jugadores(partida)
        tiradas = self.get_tiradas(turnos)

        expected_tiradas = sum(3 if turno.ultimo_turno else 2 for turno in turnos) * len(jugadores)
        return tiradas.count() >= expected_tiradas

    def finalize_game(self, partida):
        jugadores = self.get_jugadores(partida)
        puntajes = {jugador: sum(tirada.pinos_deribados for tirada in Tirada.objects.filter(id_jugador=jugador)) for jugador in jugadores}
        ganador = max(puntajes, key=puntajes.get)

        partida.ganador = ganador
        partida.estado = EstadoPartida.objects.get(estado='Finalizada')
        partida.save()
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomLoginForm

class CustomRegisterView(CreateView):
    form_class = CustomRegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')  

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        return response

def custom_logout_view(request):
    logout(request)
    return redirect('/')

class ReservaView(CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reserva.html'
    success_url = reverse_lazy('misreservas')

    def get_form_kwargs(self):
        kwargs = super(ReservaView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        reserva = form.save(commit=False)
        cliente = form.cleaned_data['email_cliente']
        reserva.id_cliente = cliente
        pista = form.cleaned_data['id_pista']
        reserva.id_pista = pista
        reserva.save()
        return super().form_valid(form)

class JugadoresView(View):
    template_name = 'cant_jugadores.html'

    def get(self, request: HttpRequest, partida_id: int, reserva_id: int):
        capacidad_maxima = self.get_capacidad_maxima(reserva_id)
        return render(request, self.template_name, {'capacidad_maxima': capacidad_maxima})

    def post(self, request: HttpRequest, partida_id: int, reserva_id: int):
        cantidad_jugadores = request.POST.get('cantidad_jugadores')
        if cantidad_jugadores:
            self.store_cantidad_jugadores(request, cantidad_jugadores)
            self.update_partida(partida_id, cantidad_jugadores)
            return redirect('nombres_jugadores', partida_id=partida_id, reserva_id=reserva_id)
        return redirect('jugadores', partida_id=partida_id, reserva_id=reserva_id)

    def get_capacidad_maxima(self, reserva_id: int) -> int:
        reserva = Reserva.objects.get(id_reserva=reserva_id)
        pista = PistaBowling.objects.get(id_pista=reserva.id_pista.id_pista)
        return pista.capacidad_maxima

    def store_cantidad_jugadores(self, request: HttpRequest, cantidad_jugadores: str):
        request.session['cantidad_jugadores'] = int(cantidad_jugadores)

    def update_partida(self, partida_id: int, cantidad_jugadores: str):
        partida = Partida.objects.filter(id_partida=partida_id).first()
        if partida:
            partida.cant_jugadores = int(cantidad_jugadores)
            partida.save()

class NombresJugadoresView(View):#MOD
    template_name = 'nombres_jugadores.html'

    def get(self, request: HttpRequest, partida_id: int, reserva_id: int):
        cantidad_jugadores = self.get_cantidad_jugadores(request)
        if self.is_valid_cantidad_jugadores(cantidad_jugadores):
            context = self.get_context(cantidad_jugadores, partida_id, reserva_id)
            return render(request, self.template_name, context)
        return redirect('jugadores', partida_id=partida_id, reserva_id=reserva_id)

    def post(self, request: HttpRequest, partida_id: int, reserva_id: int):
        if not reserva_id:
            return redirect('jugadores', partida_id=partida_id, reserva_id=reserva_id)

        partida = get_object_or_404(Partida, id_partida=partida_id)
        cantidad_jugadores = self.get_cantidad_jugadores(request)

        self.create_jugadores(request, partida, cantidad_jugadores)
        self.create_turnos(partida)
        self.update_partida_estado(partida)

        return redirect('mi_reserva', reserva_id=reserva_id)

    def get_cantidad_jugadores(self, request: HttpRequest) -> int:
        return request.session.get('cantidad_jugadores', 0)

    def is_valid_cantidad_jugadores(self, cantidad_jugadores: int) -> bool:
        return isinstance(cantidad_jugadores, int) and cantidad_jugadores > 0

    def get_context(self, cantidad_jugadores: int, partida_id: int, reserva_id: int) -> dict:
        return {
            'cantidad_jugadores': cantidad_jugadores,
            'jugadores_range': range(1, cantidad_jugadores + 1),
            'partida_id': partida_id,
            'reserva_id': reserva_id
        }

    def create_jugadores(self, request: HttpRequest, partida: Partida, cantidad_jugadores: int):
        for i in range(1, cantidad_jugadores + 1):
            nombre_jugador = request.POST.get(f'jugador{i}')
            if nombre_jugador:
                Jugador.objects.create(nombre_jugador=nombre_jugador, orden=i, id_partida=partida)

    def create_turnos(self, partida: Partida):
        for i in range(1, 11):
            Turno.objects.create(
                id_partida=partida,
                orden=i,
                ultimo_turno=(i == 10)
            )

    def update_partida_estado(self, partida: Partida):
        estado_en_proceso = EstadoPartida.objects.get(estado='En proceso')
        partida.estado = estado_en_proceso
        partida.save()

def iniciar_partida(request, partida_id):
    partida = get_object_or_404(Partida, id_partida=partida_id)
    
    id_reserva = partida.id_reserva.id_reserva

    return redirect('/jugadores/'+str(partida.id_partida)+'/' + str(id_reserva))

class AgregarPedidoView(View):#MOD
    def post(self, request: HttpRequest, reserva_id: int):
        reserva = self.get_reserva(request, reserva_id)
        productos = request.POST.getlist('producto')
        cantidades = request.POST.getlist('cantidad')

        if not self.validate_productos_cantidades(productos, cantidades):
            return JsonResponse({'success': False, 'message': 'Los productos y cantidades deben coincidir.'})

        pedido = self.create_pedido(reserva)
        self.create_pedido_productos(pedido, productos, cantidades)

        return redirect(reverse('mi_reserva', args=[reserva_id]))

    def get_reserva(self, request: HttpRequest, reserva_id: int) -> Reserva:
        return get_object_or_404(Reserva, pk=reserva_id, id_cliente=request.user.id_cliente)

    def validate_productos_cantidades(self, productos: list, cantidades: list) -> bool:
        return len(productos) == len(cantidades)

    def create_pedido(self, reserva: Reserva) -> Pedido:
        return Pedido.objects.create(
            id_reserva=reserva,
            fecha_hora_pedido=timezone.now(),
            estado=EstadoPedido.objects.get(estado='Pedido Confirmado')
        )

    def create_pedido_productos(self, pedido: Pedido, productos: list, cantidades: list):
        for producto_id, cantidad in zip(productos, cantidades):
            PedidoXProducto.objects.create(
                id_pedido=pedido,
                id_producto_id=producto_id,
                cantidad=int(cantidad)
            )


def finalizar_reserva(request, reserva_id):
    if request.method == 'POST':
        if request.user.is_superuser:
            reserva = get_object_or_404(Reserva, pk=reserva_id)
        else:
            reserva = get_object_or_404(Reserva, pk=reserva_id, id_cliente=request.user.id_cliente)
        
        estado_finalizada = EstadoReserva.objects.get(estado='Finalizada')
        
        HistorialEstado.objects.create(
            id_reserva=reserva,
            estado=estado_finalizada,
            fecha_hora_inicio=timezone.now(),
            fecha_hora_fin=timezone.now()
        )
        
        reserva.estado = estado_finalizada
        reserva.save()
        
        messages.success(request, 'Reserva finalizada exitosamente.')
        
        if request.user.is_superuser:
            return redirect(reverse('ver_reservas'))
        else:
            return redirect('mi_reserva', reserva_id=reserva_id)
    
    if request.user.is_superuser:
        return redirect(('ver_reservas'))
    else:
        return redirect('mi_reserva', reserva_id=reserva_id)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone

class VerReservasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Reserva
    template_name = 'ver.html'
    context_object_name = 'reservas'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return self.get_ordered_reservas()

    def get_ordered_reservas(self):
        return Reserva.objects.all().order_by('-fecha_hora_reserva')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_ultimo_estado_to_reservas(context['reservas'])
        return context

    def add_ultimo_estado_to_reservas(self, reservas):
        for reserva in reservas:
            reserva.ultimo_estado = self.get_ultimo_estado(reserva)

    def get_ultimo_estado(self, reserva):
        try:
            return reserva.historialestado_set.latest('fecha_hora_inicio')
        except HistorialEstado.DoesNotExist:
            return None

class EditarReservaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    form_class = ReservaEditForm
    template_name = 'editar_reserva.html'
    success_url = reverse_lazy('ver_reservas')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = self.get_all_estados()
        return context

    def get_all_estados(self):
        return EstadoReserva.objects.all()

    def form_valid(self, form):
        reserva = form.save(commit=False)
        nuevo_estado = form.cleaned_data.get('nuevo_estado')
        self.handle_historial_estado(reserva, nuevo_estado)
        self.set_success_message(nuevo_estado)
        return super().form_valid(form)

    def handle_historial_estado(self, reserva, nuevo_estado):
        self.delete_existing_historial(reserva, nuevo_estado)
        if nuevo_estado:
            self.create_new_historial(reserva, nuevo_estado)

    def delete_existing_historial(self, reserva, nuevo_estado):
        if HistorialEstado.objects.filter(id_reserva=reserva, estado=nuevo_estado).exists():
            HistorialEstado.objects.filter(id_reserva=reserva, estado=nuevo_estado).delete()

    def create_new_historial(self, reserva, nuevo_estado):
        HistorialEstado.objects.create(
            id_reserva=reserva,
            estado=nuevo_estado,
            fecha_hora_inicio=timezone.now(),
            fecha_hora_fin=reserva.fecha_hora_reserva
        )

    def set_success_message(self, nuevo_estado):
        if nuevo_estado:
            messages.success(self.request, f'Reserva actualizada y estado cambiado a {nuevo_estado}.')
        else:
            messages.success(self.request, 'Reserva actualizada exitosamente.')

class VerPedidosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Pedido
    template_name = 'ver_pedidos.html'
    context_object_name = 'pedidos'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return self.get_ordered_pedidos()

    def get_ordered_pedidos(self):
        return Pedido.objects.all().order_by('-fecha_hora_pedido')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_productos_to_pedidos(context['pedidos'])
        return context

    def add_productos_to_pedidos(self, pedidos):
        for pedido in pedidos:
            pedido.productos = self.get_productos_for_pedido(pedido)

    def get_productos_for_pedido(self, pedido):
        pedido_productos = PedidoXProducto.objects.filter(id_pedido=pedido)
        return [self.format_producto(pp) for pp in pedido_productos]

    def format_producto(self, pedido_producto):
        return {
            'nombre': pedido_producto.id_producto.nombre,
            'cantidad': pedido_producto.cantidad
        }

class EditarPedidoView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Pedido
    template_name = 'editar_pedido.html'
    fields = ['estado', 'fecha_hora_pedido', 'id_reserva']
    success_url = reverse_lazy('ver_pedidos')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        return context

    def get_title(self):
        return 'Editar Pedido'

    def form_valid(self, form):
        pedido = form.save(commit=False)
        pedido.save()
        return super().form_valid(form)

class EliminarPedidoView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Pedido
    template_name = 'eliminar_pedido.html'
    success_url = reverse_lazy('ver_pedidos')

    def test_func(self):
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        id_pedido = self.kwargs.get('pk')
        return self.get_pedido_by_id(id_pedido)

    def get_pedido_by_id(self, id_pedido):
        return get_object_or_404(Pedido, id_pedido=id_pedido)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.delete_pedido()
        return self.redirect_to_success_url(success_url)

    def delete_pedido(self):
        self.object.delete()

    def redirect_to_success_url(self, success_url):
        return HttpResponseRedirect(success_url)

class VerPistasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PistaBowling
    template_name = 'ver_pistas.html'
    context_object_name = 'pistas'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return self.get_ordered_pistas()

    def get_ordered_pistas(self):
        return PistaBowling.objects.all().order_by('id_pista')

class EditarPistaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PistaBowling
    template_name = 'editar_pista.html'
    fields = ['capacidad_maxima', 'descripcion', 'estado']
    success_url = reverse_lazy('ver_pistas')

    def test_func(self):
        return self.request.user.is_superuser