from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DeleteView, ListView, CreateView, UpdateView, View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone

from .forms import CustomLoginForm, ReservaForm, CustomRegisterForm, ReservaEditForm
from .models import *

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
        for reserva in reservas:
            reserva.procesar_reserva()
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
            estado_reserva = reserva.estado_actual
            partidas = Partida.crear_partidas_para_reserva(reserva)

            for partida in partidas:
                partida.actualizar_estado_partida(estado_reserva)

            total_a_pagar = sum(pedido.total_a_pagar for pedido in pedidos)

            context.update({
                'reserva': reserva,
                'partidas': partidas,
                'pedidos': pedidos,
                'totalAPagar': total_a_pagar,
                'estado_reserva': estado_reserva,
                'productos': Producto.objects.all(),
            })
        except Reserva.DoesNotExist:
            context.update({
                'reserva': None,
                'pedidos': None,
                'partidas': [],
                'estado_reserva': None,
            })

        return context

class TablaView(TemplateView):
    template_name = 'tabla.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        partida_id = self.kwargs['partida_id']
        partida = get_object_or_404(Partida, id_partida=partida_id)

        jugadores = partida.jugador_set.all()
        turnos = partida.turno_set.order_by('numero_turno')
        tiradas = Tirada.objects.filter(numero_turno__in=turnos)

        tiradas_dict = {}
        puntaje_jugador = {jugador.id_jugador: jugador.puntaje_total for jugador in jugadores}
        for tirada in tiradas:
            key = f"{tirada.id_jugador.id_jugador}-{tirada.numero_turno.numero_turno}"
            if key not in tiradas_dict:
                tiradas_dict[key] = []
            tiradas_dict[key].append(tirada)

        current_turn = partida.get_current_turn()

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
        jugadores = partida.jugador_set.all()
        current_turn = partida.get_current_turn()
        hay_error = False

        for jugador in jugadores:
            tiene_datos = any(
                request.POST.get(f'jugador_{jugador.id_jugador}_turno_{current_turn.numero_turno}_tirada_{j}', '')
                for j in range(1, 4 if current_turn.ultimo_turno else 3)
            )

            if not tiene_datos:
                continue

            tiradas_range = range(1, 4) if current_turn.ultimo_turno else range(1, 3)
            primera_tirada = None
            tiradas_completas = True
            tiradas_jugador = []

            for j in tiradas_range:
                clave = f'jugador_{jugador.id_jugador}_turno_{current_turn.numero_turno}_tirada_{j}'
                pinos_derribados = request.POST.get(clave, '')

                if pinos_derribados.isdigit() and not current_turn.ultimo_turno:
                    pinos_derribados = int(pinos_derribados)
                    max_pinos = 10 - (primera_tirada.pinos_deribados if primera_tirada else 0)

                    if 0 <= pinos_derribados <= max_pinos:
                        tirada = Tirada.registrar_tirada(jugador, current_turn, pinos_derribados, j)
                        tiradas_jugador.append(tirada)
                        if j == 1:
                            primera_tirada = tirada
                    else:
                        messages.error(request, f"⦁ Turno {current_turn.orden} invalido para el jugador {jugador.nombre_jugador}, tirada {j}: Es imposible tirar mas de 10 pinos.")
                        tiradas_completas = False
                        hay_error = True
                        break
                elif pinos_derribados == '':
                    tiradas_completas = False
                    hay_error = True
                    break
                elif current_turn.ultimo_turno:
                    tirada = Tirada.registrar_tirada(jugador, current_turn, pinos_derribados, j)
                    tiradas_jugador.append(tirada)
                    tiradas_completas = True
                    hay_error = False
                else:
                    messages.error(request, f"⦁ Turno {current_turn.orden} invalido para el jugador {jugador.nombre_jugador}, fila {j}: Debe ser un numero.")
                    tiradas_completas = False
                    hay_error = True
                    break

            if not tiradas_completas:
                for tirada in tiradas_jugador:
                    tirada.delete()
                messages.error(request, f"⦁ Todas las tiradas deben ser registradas por el jugador {jugador.nombre_jugador} en el turno {current_turn.orden}.")

        if not hay_error and partida.is_game_finished():
            partida.finalize_game()
            return redirect('mi_reserva', reserva_id=partida.id_reserva.id_reserva)

        return redirect('tabla', partida_id=partida_id)

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
        messages.success(self.request, 'Reserva creada exitosamente.')
        return super().form_valid(form)

class JugadoresView(View):
    def get(self, request, partida_id, reserva_id):
        reserva = Reserva.objects.get(id_reserva=reserva_id)
        pista = reserva.id_pista
        capacidad_maxima = pista.capacidad_maxima  
        
        return render(request, 'cant_jugadores.html', {'capacidad_maxima': capacidad_maxima})

    def post(self, request, partida_id, reserva_id):
        cantidad_jugadores = request.POST.get('cantidad_jugadores')
        if cantidad_jugadores:
            request.session['cantidad_jugadores'] = int(cantidad_jugadores)
            
            partida = Partida.objects.filter(id_partida=partida_id).first()
            if partida:
                partida.cant_jugadores = int(cantidad_jugadores)
                partida.save()

            return redirect('nombres_jugadores', partida_id=partida_id, reserva_id=reserva_id)
        return redirect('jugadores', partida_id=partida_id, reserva_id=reserva_id)

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
                Jugador.objects.create(nombre_jugador=nombre_jugador, orden=i, id_partida=partida)
        
        partida.crear_turnos()
        partida.iniciar_partida()

        return redirect('mi_reserva', reserva_id=reserva_id)

def iniciar_partida(request, partida_id):
    partida = get_object_or_404(Partida, id_partida=partida_id)
    id_reserva = partida.id_reserva.id_reserva
    return redirect('/jugadores/'+str(partida.id_partida)+'/' + str(id_reserva))

class AgregarPedidoView(View):
    def post(self, request, reserva_id):
        reserva = get_object_or_404(Reserva, pk=reserva_id, id_cliente=request.user.id_cliente)

        productos = request.POST.getlist('producto')
        cantidades = request.POST.getlist('cantidad')

        if len(productos) != len(cantidades):
            return JsonResponse({'success': False, 'message': 'Los productos y cantidades deben coincidir.'})

        Pedido.crear_pedido(reserva, productos, cantidades)

        return redirect(reverse('mi_reserva', args=[reserva_id]))

def finalizar_reserva(request, reserva_id):
    if request.method == 'POST':
        if request.user.is_superuser:
            reserva = get_object_or_404(Reserva, pk=reserva_id)
        else:
            reserva = get_object_or_404(Reserva, pk=reserva_id, id_cliente=request.user.id_cliente)
        
        reserva.finalizar()
        
        messages.success(request, 'Reserva finalizada exitosamente.')
        
        if request.user.is_superuser:
            return redirect(reverse('ver_reservas'))
        else:
            return redirect('mi_reserva', reserva_id=reserva_id)
    
    if request.user.is_superuser:
        return redirect(('ver_reservas'))
    else:
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
            reserva.actualizar_ultimo_estado()
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
            reserva.crear_historial_estado(nuevo_estado, timezone.now(), reserva.fecha_hora_reserva)
            messages.success(self.request, f'Reserva actualizada y estado cambiado a {nuevo_estado}.')
        else:
            messages.success(self.request, 'Reserva actualizada exitosamente.')
        
        return super().form_valid(form)

class VerPedidosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Pedido
    template_name = 'ver_pedidos.html'
    context_object_name = 'pedidos'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return Pedido.objects.all().order_by('-fecha_hora_pedido')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pedidos = context['pedidos']
        for pedido in pedidos:
            pedido_productos = PedidoXProducto.objects.filter(id_pedido=pedido)
            pedido.productos = [
                {
                    'nombre': pp.id_producto.nombre,
                    'cantidad': pp.cantidad
                }
                for pp in pedido_productos
            ]
        return context

class EditarPedidoView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Pedido
    template_name = 'editar_pedido.html'
    fields = ['estado', 'fecha_hora_pedido', 'id_reserva']
    success_url = reverse_lazy('ver_pedidos')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Pedido'
        return context

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
        return get_object_or_404(Pedido, id_pedido=id_pedido)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

class VerPistasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PistaBowling
    template_name = 'ver_pistas.html'
    context_object_name = 'pistas'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return PistaBowling.objects.all().order_by('id_pista')

class EditarPistaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PistaBowling
    template_name = 'editar_pista.html'
    fields = ['capacidad_maxima', 'descripcion', 'estado']
    success_url = reverse_lazy('ver_pistas')

    def test_func(self):
        return self.request.user.is_superuser