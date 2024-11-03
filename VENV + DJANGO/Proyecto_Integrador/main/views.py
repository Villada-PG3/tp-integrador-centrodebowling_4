#_____________________________________________________
#_____________ IMPORTS__________________________________
#_____________________________________________________



from django.shortcuts import render



from django.views.generic import TemplateView
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

from django.http import JsonResponse

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

#_____________________________________________________
#_____________ VIEWS__________________________________
#_____________________________________________________

class IndexView(TemplateView):
    template_name = 'index.html'

class MisReservasView(ListView):
    model = Reserva
    template_name = 'misreservas.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        reservas = Reserva.objects.filter(id_cliente=self.request.user.id_cliente)
        ahora = timezone.now()  # Obtener la fecha y hora actual

        for reserva in reservas:
            print(f"Reserva ID: {reserva.id_reserva}, fecha_hora_reserva: {reserva.fecha_hora_reserva}, fecha_hora_fin: {reserva.fecha_hora_fin}")
            try:
                reserva.ultimo_estado = reserva.historialestado_set.latest('fecha_hora_inicio')
            except HistorialEstado.DoesNotExist:
                reserva.ultimo_estado = None

            # Verificar si la reserva está confirmada
            estado_default = EstadoReserva.objects.get(estado='Confirmada')
            if not HistorialEstado.objects.filter(id_reserva=reserva, estado=estado_default).exists():
                HistorialEstado.objects.create(
                    id_reserva=reserva,
                    estado=estado_default,
                    fecha_hora_inicio=ahora,
                    fecha_hora_fin=ahora + timedelta(hours=2)  # Guardar como DateTimeField
                )

            # Verificar el estado actual de la reserva
            if reserva.fecha_hora_reserva and reserva.fecha_hora_reserva <= ahora:
                # Cambiar a 'En Curso'
                estado_en_curso = EstadoReserva.objects.get(estado='En Curso')
                if reserva.ultimo_estado.estado.estado == 'Confirmada':
                    HistorialEstado.objects.create(
                        id_reserva=reserva,
                        estado=estado_en_curso,
                        fecha_hora_inicio=ahora,
                        fecha_hora_fin=ahora + timedelta(hours=2)  # Guardar como DateTimeField
                    )

            # Verificar si la reserva ha finalizado
            if reserva.fecha_hora_fin and reserva.fecha_hora_reserva <= ahora and reserva.fecha_hora_fin <= ahora.time():
                # Cambiar a 'Finalizada'
                estado_finalizada = EstadoReserva.objects.get(estado='Finalizada')
                if reserva.ultimo_estado.estado.estado == 'En Curso':
                    HistorialEstado.objects.create(
                        id_reserva=reserva,
                        estado=estado_finalizada,
                        fecha_hora_inicio=ahora,
                        fecha_hora_fin=ahora  # Guardar como DateTimeField
                    )

            # Actualizar la fecha_hora_fin aquí si es necesario
            if reserva.fecha_hora_reserva:
                hora_final = reserva.fecha_hora_reserva + timedelta(hours=2)
                reserva.fecha_hora_fin = hora_final.time()  # Guardar solo la parte de la hora
                reserva.save()

        return reservas

def cancelar_reserva(request, pk):
    reserva = Reserva.objects.get(pk=pk)
    reserva.delete()
    return redirect('misreservas')

class ContactoView(TemplateView):
    template_name = 'contacto.html'

class mi_reserva(TemplateView):
    template_name = 'menu_partidas_bar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reserva_id = self.kwargs['reserva_id']

        try:
            reserva = get_object_or_404(Reserva, pk=reserva_id, id_cliente=self.request.user.id_cliente)
            pedidos = Pedido.objects.filter(id_reserva=reserva.id_reserva)

            # Obtener el último estado de la reserva
            try:
                ultimo_estado = reserva.historialestado_set.latest('fecha_hora_inicio')
                estado_reserva = ultimo_estado.estado.estado
            except HistorialEstado.DoesNotExist:
                estado_reserva = 'Confirmada'

            # Obtener o crear las 3 partidas para la reserva
            partidas = list(Partida.objects.filter(id_reserva=reserva).order_by('id_partida'))
            if len(partidas) < 3:
                estado_bloqueado = EstadoPartida.objects.get(estado='Bloqueada')
                for _ in range(3 - len(partidas)):
                    nueva_partida = Partida.objects.create(
                        id_pista=reserva.id_pista,
                        id_reserva=reserva,
                        estado=estado_bloqueado,
                        cant_jugadores=0
                    )
                    partidas.append(nueva_partida)

            # Actualizar los estados de las partidas
            estado_disponible = EstadoPartida.objects.get(estado='Disponible')
            estado_bloqueado = EstadoPartida.objects.get(estado='Bloqueada')
            estado_en_proceso = EstadoPartida.objects.get(estado='En proceso')
            estado_finalizado = EstadoPartida.objects.get(estado='Finalizada')

            for i, partida in enumerate(partidas):
                if estado_reserva == 'En curso':
                    if i == 0 and partida.estado != estado_finalizado and partida.estado != estado_en_proceso:
                        partida.estado = estado_disponible
                    elif i > 0 and partidas[i-1].estado == estado_finalizado and partida.estado != estado_finalizado and partida.estado != estado_en_proceso:
                        partida.estado = estado_disponible
                    elif partida.estado != estado_finalizado and partida.estado != estado_en_proceso:
                        partida.estado = estado_bloqueado
                else:
                    if partida.estado != estado_finalizado and partida.estado != estado_en_proceso:
                        partida.estado = estado_bloqueado

                if partida.estado == estado_finalizado:
                    jugadores = Jugador.objects.filter(id_partida=partida)
                    if jugadores.exists():
                        puntajes = {jugador: sum(tirada.pinos_deribados for tirada in jugador.tirada_set.all()) for jugador in jugadores}
                        ganador = max(puntajes, key=puntajes.get)
                        partida.ganador = ganador

                partida.save()

            # Calcular el total a pagar por todos los pedidos
            total_a_pagar = 0
            for pedido in pedidos:
                for item in pedido.pedidoxproducto_set.all():
                    total_a_pagar += item.cantidad * item.id_producto.precio

            context['reserva'] = reserva
            context['partidas'] = partidas
            context['pedidos'] = pedidos
            context['totalAPagar'] = total_a_pagar
            context['estado_reserva'] = estado_reserva
            context['productos'] = Producto.objects.all()
            
        except Reserva.DoesNotExist:
            context['reserva'] = None
            context['pedidos'] = None
            context['partidas'] = []
            context['estado_reserva'] = None
        
        return context

class TablaView(TemplateView):
    template_name = 'tabla.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partida_id = self.kwargs['partida_id']
        partida = get_object_or_404(Partida, id_partida=partida_id)

        jugadores = Jugador.objects.filter(id_partida=partida)
        turnos = Turno.objects.filter(id_partida=partida).order_by('numero_turno')
        tiradas = Tirada.objects.filter(numero_turno__in=turnos)

        tiradas_dict = {}
        puntaje_jugador = {jugador.id_jugador: 0 for jugador in jugadores}
        for tirada in tiradas:
            key = f"{tirada.id_jugador.id_jugador}-{tirada.numero_turno.numero_turno}"
            if key not in tiradas_dict:
                tiradas_dict[key] = []
            tiradas_dict[key].append(tirada)
            puntaje_jugador[tirada.id_jugador.id_jugador] += tirada.pinos_deribados

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
        partida = get_object_or_404(Partida, id_partida=partida_id)
        jugadores = Jugador.objects.filter(id_partida=partida)
        current_turn = self.get_current_turn(partida)

        for jugador in jugadores:
            tiradas_range = range(1, 4) if current_turn.ultimo_turno else range(1, 3)
            for j in tiradas_range:
                clave = f'jugador_{jugador.id_jugador}_turno_{current_turn.numero_turno}_tirada_{j}'
                pinos_derribados = request.POST.get(clave, '')

                if pinos_derribados.isdigit():
                    pinos_derribados = int(pinos_derribados)
                    if 0 <= pinos_derribados <= 10:
                        Tirada.objects.create(
                            pinos_deribados=pinos_derribados,
                            orden=j,
                            id_jugador=jugador,
                            numero_turno=current_turn,
                        )
                    else:
                        messages.error(request, f"Invalid input for {jugador.nombre_jugador}, turn {current_turn.numero_turno}, throw {j}: Must be between 0 and 10.")
                elif pinos_derribados != '':
                    messages.error(request, f"Invalid input for {jugador.nombre_jugador}, turn {current_turn.numero_turno}, throw {j}: Must be a number.")

        if self.is_game_finished(partida):
            self.finalize_game(partida)
            return redirect('mi_reserva', reserva_id=partida.id_reserva.id_reserva)

        return redirect('tabla', partida_id=partida_id)

    def get_current_turn(self, partida):
        turnos = Turno.objects.filter(id_partida=partida).order_by('numero_turno')
        tiradas = Tirada.objects.filter(numero_turno__in=turnos)
        tiradas_count = tiradas.count()
        jugadores_count = Jugador.objects.filter(id_partida=partida).count()
        
        current_turn_index = tiradas_count // (2 * jugadores_count)
        if current_turn_index < len(turnos):
            return turnos[current_turn_index]
        else:
            return turnos.last()

    def is_game_finished(self, partida):
        turnos = Turno.objects.filter(id_partida=partida)
        jugadores = Jugador.objects.filter(id_partida=partida)
        tiradas = Tirada.objects.filter(numero_turno__in=turnos)

        expected_tiradas = sum(3 if turno.ultimo_turno else 2 for turno in turnos) * len(jugadores)
        return tiradas.count() >= expected_tiradas

    def finalize_game(self, partida):
        jugadores = Jugador.objects.filter(id_partida=partida)
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
    def get(self, request, partida_id, reserva_id):
        # Obtener la capacidad máxima de la pista
        capacidad_maxima = request.session.get('capacidad_maxima', 10)  # Cambia el valor por defecto si es necesario
        # Puedes usar reserva_id si lo necesitas para algo
        return render(request, 'cant_jugadores.html', {'capacidad_maxima': capacidad_maxima})

    def post(self, request, partida_id, reserva_id):
        cantidad_jugadores = request.POST.get('cantidad_jugadores')
        if cantidad_jugadores:
            request.session['cantidad_jugadores'] = int(cantidad_jugadores)  # Asegúrate de almacenar como int
            
            # Actualizar la cantidad de jugadores en la partida correspondiente
            partida = Partida.objects.filter(id_partida=partida_id).first()  # Obtener la partida usando el id_partida
            if partida:
                partida.cant_jugadores = int(cantidad_jugadores)
                partida.save()

            return redirect('nombres_jugadores', partida_id=partida_id, reserva_id=reserva_id)  # Redirige a la vista de nombres de jugadores
        return redirect('jugadores', partida_id=partida_id, reserva_id=reserva_id)  # Redirigir si no hay cantidad válida

class NombresJugadoresView(View):
    def get(self, request, partida_id, reserva_id):
        cantidad_jugadores = request.session.get('cantidad_jugadores', 0)
        if isinstance(cantidad_jugadores, int) and cantidad_jugadores > 0:
            context = {
                'cantidad_jugadores': cantidad_jugadores,
                'jugadores_range': range(1, cantidad_jugadores + 1),
                'partida_id': partida_id,
                'reserva_id': reserva_id
            }
            return render(request, 'nombres_jugadores.html', context)
        else:
            return redirect('jugadores', partida_id=partida_id, reserva_id=reserva_id)

    def post(self, request, partida_id, reserva_id):
        cantidad_jugadores = request.session.get('cantidad_jugadores', 0)

        if not reserva_id:
            return redirect('jugadores', partida_id=partida_id, reserva_id=reserva_id)

        partida = get_object_or_404(Partida, id_partida=partida_id)

        for i in range(1, cantidad_jugadores + 1):
            nombre_jugador = request.POST.get(f'jugador{i}')
            if nombre_jugador:
                jugador = Jugador(nombre_jugador=nombre_jugador, orden=i, id_partida=partida)
                jugador.save()
        
        for i in range(1, 11):
            Turno.objects.create(
                id_partida=partida,
                orden=i,
                ultimo_turno=(i == 10)
            )
        
        # Update the game state to 'En proceso'
        estado_en_proceso = EstadoPartida.objects.get(estado='En proceso')
        partida.estado = estado_en_proceso
        partida.save()

        return redirect('mi_reserva', reserva_id=reserva_id)

def iniciar_partida(request, partida_id):
    partida = get_object_or_404(Partida, id_partida=partida_id)
    
    id_reserva = partida.id_reserva.id_reserva

    return redirect('/jugadores/'+str(partida.id_partida)+'/' + str(id_reserva))

class AgregarPedidoView(View):
    def post(self, request, reserva_id):
        reserva = get_object_or_404(Reserva, pk=reserva_id, id_cliente=request.user.id_cliente)

        # Aquí asumimos que los datos del formulario vienen en un formato específico
        productos = request.POST.getlist('producto')
        cantidades = request.POST.getlist('cantidad')

        if len(productos) != len(cantidades):
            return JsonResponse({'success': False, 'message': 'Los productos y cantidades deben coincidir.'})

        # Crear el pedido
        pedido = Pedido.objects.create(
            id_reserva=reserva,
            fecha_hora_pedido=timezone.now(),
            estado=EstadoPedido.objects.get(estado='Pedido Confirmado')  # Asignar estado inicial
        )

        # Guardar cada producto y cantidad en PedidoXProducto
        for producto_id, cantidad in zip(productos, cantidades):
            PedidoXProducto.objects.create(
                id_pedido=pedido,
                id_producto_id=producto_id,
                cantidad=int(cantidad)
            )

        return redirect('mi_reserva', reserva_id)

def finalizar_reserva(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, pk=reserva_id, id_cliente=request.user.id_cliente)
        estado_finalizada = EstadoReserva.objects.get(estado='Finalizada')
        
        HistorialEstado.objects.create(
            id_reserva=reserva,
            estado=estado_finalizada,
            fecha_hora_inicio=timezone.now(),
            fecha_hora_fin=timezone.now()
        )
        
        messages.success(request, 'Reserva finalizada exitosamente.')
        return redirect('mi_reserva', reserva_id=reserva_id)
    
    return redirect('mi_reserva', reserva_id=reserva_id)

class VerReservasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Reserva
    template_name = 'ver.html'
    context_object_name = 'reservas'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return Reserva.objects.all().order_by('-fecha_hora_reserva')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for reserva in context['reservas']:
            try:
                reserva.ultimo_estado = reserva.historialestado_set.latest('fecha_hora_inicio')
            except HistorialEstado.DoesNotExist:
                reserva.ultimo_estado = None
        return context

class EditarReservaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    form_class = ReservaEditForm
    template_name = 'editar_reserva.html'
    success_url = reverse_lazy('ver_reservas')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = EstadoReserva.objects.all()
        return context

    def form_valid(self, form):
        reserva = form.save(commit=False)
        nuevo_estado = form.cleaned_data.get('nuevo_estado')
        
        if nuevo_estado:
            HistorialEstado.objects.create(
                id_reserva=reserva,
                estado=nuevo_estado,
                fecha_hora_inicio=timezone.now(),
                fecha_hora_fin=reserva.fecha_hora_reserva
            )
            messages.success(self.request, f'Reserva actualizada y estado cambiado a {nuevo_estado}.')
        else:
            messages.success(self.request, 'Reserva actualizada exitosamente.')
        
        return super().form_valid(form)

