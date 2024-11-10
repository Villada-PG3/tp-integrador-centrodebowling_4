
#=============================================================================================
#============================  IMPORTS =======================================================
#=============================================================================================


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

#====================== VIEWS + LOGICA ========================================================


class IndexView(TemplateView): # View de Inicio, html puro
    template_name = 'index.html' #nombre de la plantilla a usar

class MisReservasView(ListView): #La view para ver tus Reservas
    model = Reserva
    template_name = 'misreservas.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated: #Aca hace que si el usuario no inicio sesion, lo mande al login
            return redirect('login')
        return super().get(request, *args, **kwargs) #Si inicio sesion, entonces obtiene los argumentos del html

    def get_queryset(self):
        reservas = Reserva.get_reserva_x_cliente(self, self.request.user.id_cliente)# obtiene las reservas del usuario logueado
        for reserva in reservas:
            reserva.procesar_reserva() # checkea todos los datos de la reserva
        return reservas

def cancelar_reserva(request, pk): # Pa cancelar la reserva
    reserva = Reserva.objects.get(pk=pk)
    reserva.delete()
    return redirect('misreservas')

class ContactoView(TemplateView): # Puro html
    template_name = 'contacto.html'

class mi_reserva(TemplateView): #cuando le das al boton de "ver" en la lista de mis reservas, donde ves las partidas y gestionas tus pedidos
    template_name = 'menu_partidas_bar.html'

    def get_context_data(self, **kwargs): #obtiene
        context = super().get_context_data(**kwargs)
        reserva_id = self.kwargs['reserva_id']

        try:
            reserva = get_object_or_404(Reserva, pk=reserva_id, id_cliente=self.request.user.id_cliente)
            pedidos = Pedido.obtener_pedidos_reserva(self, reserva.id_reserva) #obtiene los pedidos de la reserva
            estado_reserva = reserva.estado_actual
            partidas = Partida.crear_partidas_para_reserva(reserva) # le crea las 3 partidas correspondientes

            for partida in partidas:
                partida.update_partidas_status(partidas, estado_reserva) #actualiza el estado de la reserva

            total_a_pagar = sum(pedido.total_a_pagar for pedido in pedidos)

          # Agrega al contexto la información necesaria para la vista de la reserva
            context.update({
                'reserva': reserva,              # Datos de la reserva actual
                'partidas': partidas,            # Partidas asociadas a la reserva
                'pedidos': pedidos,              # Pedidos realizados en la reserva
                'totalAPagar': total_a_pagar,    # Monto total a pagar
                'estado_reserva': estado_reserva,# Estado de la reserva (ej., "Confirmada")
                'productos': Producto.objects.all(), # Todos los productos disponibles
            })
        except Reserva.DoesNotExist:   #en el caso de no tener datos se agrega none
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
        partida_id = self.kwargs['partida_id'] # Agarra el ID de la partida desde los parámetros de la URL.
        partida = get_object_or_404(Partida, id_partida=partida_id)

        # Trae todos los jugadores, turnos y tiradas que están relacionados con esta partida
        jugadores = partida.jugador_set.all()
        turnos = partida.turno_set.order_by('numero_turno')
        tiradas = Tirada.objects.filter(numero_turno__in=turnos)

        # Acá se crea un diccionario para agrupar las tiradas de cada jugador en cada turno
        tiradas_dict = {}
        puntaje_jugador = {jugador.id_jugador: jugador.puntaje_total for jugador in jugadores}
        for tirada in tiradas:
            key = f"{tirada.id_jugador.id_jugador}-{tirada.numero_turno.numero_turno}"  # Cada clave en este diccionario es una combinación de jugador y turno 
            if key not in tiradas_dict:
                tiradas_dict[key] = []
            tiradas_dict[key].append(tirada)
            

        current_turn = partida.get_current_turn() # Agarra el turno actual de la partida para ver quién juega ahora

         # Actualiza el contexto con toda la info que vamos a usar en la vista
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
    
      # Esta función maneja el envío de datos para registrar las tiradas de los jugadores.
    def post(self, request, partida_id): 
        partida = get_object_or_404(Partida, id_partida=partida_id)
        jugadores = partida.jugador_set.all()
        current_turn = partida.get_current_turn()
        hay_error = False

        for jugador in jugadores:
             # Verifica si el jugador ingresó algo para al menos una tirada en el turno actual
            tiene_datos = any(
                request.POST.get(f'jugador_{jugador.id_jugador}_turno_{current_turn.numero_turno}_tirada_{j}', '')
                for j in range(1, 4 if current_turn.ultimo_turno else 3)
            )

            if not tiene_datos:
                continue
            # Define cuántas tiradas pueden hacerse
            tiradas_range = range(1, 4) if current_turn.ultimo_turno else range(1, 3)
            primera_tirada = None
            tiradas_completas = True
            tiradas_jugador = []

            for j in tiradas_range:
                 # Acá agarra el valor de pinos tirados que puso el usuario en el formulario
                clave = f'jugador_{jugador.id_jugador}_turno_{current_turn.numero_turno}_tirada_{j}'
                pinos_derribados = request.POST.get(clave, '')
                
                # Si el usuario pone 'x', lo interpretamos como 10 (un strike)
                if pinos_derribados == 'x':
                    pinos_derribados = '10'
                
                # Verificación y registro de tiradas en turnos comunes (no el último)
                if pinos_derribados.isdigit() and not current_turn.ultimo_turno:

                     # Asegura que la cantidad de pinos no pase de 10 o lo que queda después de la primera tirada
                    pinos_derribados = int(pinos_derribados)
                    max_pinos = 10 - (primera_tirada.pinos_deribados if primera_tirada else 0)

                    if 0 <= pinos_derribados <= max_pinos:
                         #Si la tirada es válida, se guarda en la base de datos y se agrega a la lista de tiradas de este jugador
                        tirada = Tirada.registrar_tirada(jugador, current_turn, pinos_derribados, j)
                        tiradas_jugador.append(tirada)
                        if j == 1:
                            primera_tirada = tirada
                    else:
                        # Muestra un mensaje de error si el valor de pinos es inválido (más de 10).
                        messages.success(request, f"⦁ Turno {current_turn.orden} invalido para el jugador {jugador.nombre_jugador}, tirada {j}: Es imposible tirar mas de 10 pinos.")
                        tiradas_completas = False
                        hay_error = True
                        break

                elif pinos_derribados == '':
                    # Marca como incompleta si falta un valor de tirada
                    tiradas_completas = False
                    hay_error = True
                    break
                elif current_turn.ultimo_turno:
                    tirada = Tirada.registrar_tirada(jugador, current_turn, pinos_derribados, j)
                    tiradas_jugador.append(tirada)
                    tiradas_completas = True
                    hay_error = False
                else:
                    # Muestra un mensaje si el valor no es un número
                    messages.success(request, f"⦁ Turno {current_turn.orden} invalido para el jugador {jugador.nombre_jugador}, fila {j}: Debe ser un numero.")
                    tiradas_completas = False
                    hay_error = True
                    break

            if not tiradas_completas:
                # Borra todas las tiradas si no completó correctamente
                for tirada in tiradas_jugador:
                    tirada.delete()
                messages.success(request, f"⦁ Todas las tiradas deben ser registradas por el jugador {jugador.nombre_jugador} en el turno {current_turn.orden}.")

        if not hay_error and partida.is_game_finished():
            partida.finalize_game(partida)
            return redirect('mi_reserva', reserva_id=partida.id_reserva.id_reserva)
         # Si hay errores o el juego sigue, redirige de nuevo a la tabla de esta partida.
        return redirect('tabla', partida_id=partida_id)
    
# Vista de login personalizada que usa el template
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomLoginForm #Nuestra clase de login

# Vista para crear un nuevo usuario
class CustomRegisterView(CreateView):
    form_class = CustomRegisterForm #Clase de registro
    template_name = 'register.html' #Especificamos la plantilla
    success_url = reverse_lazy('login') #Cuando se registra redirige al login

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        return response

# Vista personalizada para cerrar sesión.
def custom_logout_view(request):
    logout(request)  # Cierra la sesión del usuario actual.
    return redirect('/')  # Redirige al usuario a la página de inicio ("/") después de desloguearse.

# Vista para crear una reserva
class ReservaView(CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reserva.html'
    success_url = reverse_lazy('misreservas') # Redirige a la página 'misreservas' al completar la reserva

    def get_form_kwargs(self):
        kwargs = super(ReservaView, self).get_form_kwargs()
        kwargs['request'] = self.request # Agrega el request a los argumentos del formulario
        return kwargs

    def form_valid(self, form):
        #Asigna todos los datos para luego guardarlos en reserva
        reserva = form.save(commit=False)
        cliente = form.cleaned_data['email_cliente']
        reserva.id_cliente = cliente
        pista = form.cleaned_data['id_pista']
        reserva.id_pista = pista

        
        reserva.save()
        
        return super().form_valid(form)

class JugadoresView(View):
    def get(self, request, partida_id, reserva_id):
        reserva = Reserva.objects.get(id_reserva=reserva_id) # Conseguimos la reserva a partir del ID
        pista = reserva.id_pista
        capacidad_maxima = pista.capacidad_maxima  
        
        return render(request, 'cant_jugadores.html', {'capacidad_maxima': capacidad_maxima}) #Muestra capacidad maxima

    def post(self, request, partida_id, reserva_id):
        cantidad_jugadores = request.POST.get('cantidad_jugadores')
        if cantidad_jugadores: # Guardamos la cantidad de jugadores en la sesión
            request.session['cantidad_jugadores'] = int(cantidad_jugadores)
            
            # Buscamos la partida y actualizamos la cantidad de jugadores
            partida = Partida.objects.filter(id_partida=partida_id).first()
            if partida:
                partida.cant_jugadores = int(cantidad_jugadores)
                partida.save()

            return redirect('nombres_jugadores', partida_id=partida_id, reserva_id=reserva_id)
        return redirect('jugadores', partida_id=partida_id, reserva_id=reserva_id)

class NombresJugadoresView(View):  #Vista encargada de gestionar los nombres de los jugadores en una partida
    def get(self, request, partida_id, reserva_id):
        cantidad_jugadores = request.session.get('cantidad_jugadores', 0)
        if isinstance(cantidad_jugadores, int) and cantidad_jugadores > 0:  # Verificamos que la cantidad de jugadores sea válida
            # Preparamos el contexto con la cantidad de jugadores
            context = {
                'cantidad_jugadores': cantidad_jugadores,
                'jugadores_range': range(1, cantidad_jugadores + 1),
                'partida_id': partida_id,
                'reserva_id': reserva_id
            }
              # Renderizamos la plantilla con el contexto
            return render(request, 'nombres_jugadores.html', context)
        else:
              # Si no hay una cantidad de jugadores válida, redirigimos a la página de selección de jugadores
            return redirect('jugadores', partida_id=partida_id, reserva_id=reserva_id)

    def post(self, request, partida_id, reserva_id):
        cantidad_jugadores = request.session.get('cantidad_jugadores', 0)

        if not reserva_id:  # Si no se tiene el ID de reserva, redirigimos a la página de selección de jugadores
            return redirect('jugadores', partida_id=partida_id, reserva_id=reserva_id)

        partida = get_object_or_404(Partida, id_partida=partida_id)

        for i in range(1, cantidad_jugadores + 1): #Creamos el jugador
            nombre_jugador = request.POST.get(f'jugador{i}')
            if nombre_jugador:
                Jugador.objects.create(nombre_jugador=nombre_jugador, orden=i, id_partida=partida)
        
        partida.crear_turnos()
        partida.iniciar_partida()

        return redirect('mi_reserva', reserva_id=reserva_id) # Redirigimos a la vista de la reserva

def iniciar_partida(request, partida_id):
    partida = get_object_or_404(Partida, id_partida=partida_id) # Obtenemos la partida correspondiente al ID
    id_reserva = partida.id_reserva.id_reserva # Extraemos el ID de la reserva asociada a esta partida
    return redirect('/jugadores/'+str(partida.id_partida)+'/' + str(id_reserva))

class AgregarPedidoView(View):
    # Metodo para agregar pedido
    def post(self, request, reserva_id):
        reserva = get_object_or_404(Reserva, pk=reserva_id, id_cliente=request.user.id_cliente) # Buscamos la reserva por su ID
         # Obtenemos los productos y cantidades enviadas desde el formulario
        productos = request.POST.getlist('producto')
        cantidades = request.POST.getlist('cantidad')

        if len(productos) != len(cantidades): # Comprobamos que el número de productos y cantidades coincidan
            return JsonResponse({'success': False, 'message': 'Los productos y cantidades deben coincidir.'})

        Pedido.crear_pedido(reserva, productos, cantidades)

        return redirect(reverse('mi_reserva', args=[reserva_id]))
# Vista para finalizar la reserva.
def finalizar_reserva(request, reserva_id):
    if request.method == 'POST':
        if request.user.is_superuser: # Si el usuario es administrador (superusuario), puede finalizar cualquier reserva
            reserva = get_object_or_404(Reserva, pk=reserva_id)
        else:
            reserva = get_object_or_404(Reserva, pk=reserva_id, id_cliente=request.user.id_cliente)# Si no es administrador, solo puede finalizar la reserva si es el cliente dueño de la reserva   
        
        reserva.finalizar()

        if request.user.is_superuser:
            return redirect(reverse('ver_reservas')) # Todas las reservas
        else:
            return redirect('mi_reserva', reserva_id=reserva_id) # Mis reservas
    
    if request.user.is_superuser:
        return redirect(('ver_reservas'))
    else:
        return redirect('mi_reserva', reserva_id=reserva_id)

class VerReservasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Reserva  # Especifica el modelo de datos a usar
    template_name = 'ver.html'  
    context_object_name = 'reservas'  # Define el nombre que se usará para acceder a las reservas en el template

    def test_func(self):
        # Verifica si el usuario es un superusuario
        return self.request.user.is_superuser

    def get_queryset(self):
        # Devuelve el conjunto de datos de reservas
        return Reserva.objects.all().order_by('-fecha_hora_reserva')

    def get_context_data(self, **kwargs):
        # Añade datos adicionales al contexto de la vista
        context = super().get_context_data(**kwargs)
        for reserva in context['reservas']:
            reserva.actualizar_ultimo_estado()  # Llama al método actualizar_ultimo_estado
        return context

class EditarReservaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    form_class = ReservaEditForm
    template_name = 'editar_reserva.html'
    success_url = reverse_lazy('ver_reservas')# Define la URL a la que redirigir después de editar


    def test_func(self):
        # Verifica si el usuario es un superusuario
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        # Añade datos de estado de reserva al contexto
        context = super().get_context_data(**kwargs)
        context['estados'] = EstadoReserva.objects.all()
        return context

    def form_valid(self, form):
        # Si el formulario es válido, guarda la reserva
        reserva = form.save(commit=False)
        nuevo_estado = form.cleaned_data.get('nuevo_estado')
        if nuevo_estado:
            # Si hay un nuevo estado lo registra
            reserva.crear_historial_estado(nuevo_estado, timezone.now(), reserva.fecha_hora_reserva)
        return super().form_valid(form)

class VerPedidosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Pedido
    template_name = 'ver_pedidos.html'
    context_object_name = 'pedidos'

    def test_func(self):
        # Verifica si es superusuario
        return self.request.user.is_superuser

    def get_queryset(self):
        # Devuelve todos los pedidos
        return Pedido.objects.all().order_by('-fecha_hora_pedido')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pedidos = context['pedidos'] # Obtiene toda la lista de pedidos
        # Se obtiene todos los productos de un pedido
        for pedido in pedidos:
            pedido_productos = PedidoXProducto.objects.filter(id_pedido=pedido)
            # Asocia la lista de productos con su nombre y cantidad
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
    success_url = reverse_lazy('ver_pedidos') #redirige a ver_pedidos

    def test_func(self):
        # Verifica si es superusuario
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Pedido'
        return context

    def form_valid(self, form):
        # Este método guarda los cambios realizados en el formulario
        pedido = form.save(commit=False) # Guarda el pedido
        pedido.save() # Guarda el pedido en la DB
        return super().form_valid(form)

class EliminarPedidoView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Pedido
    template_name = 'eliminar_pedido.html'
    success_url = reverse_lazy('ver_pedidos')

    def test_func(self):
        # Verifica si es superusuario
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        id_pedido = self.kwargs.get('pk')
        return get_object_or_404(Pedido, id_pedido=id_pedido) # Si no encuentra devuelve error

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()  # Obtiene el objeto que se va a eliminar
        success_url = self.get_success_url()  # Obtiene la URL de éxito después de la eliminación
        self.object.delete()  # Elimina el pedido de la base de datos
        return HttpResponseRedirect(success_url)  # Redirige a la URL

class VerPistasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PistaBowling
    template_name = 'ver_pistas.html'
    context_object_name = 'pistas'

    def test_func(self):
        # Verifica si es superusuario
        return self.request.user.is_superuser

    def get_queryset(self):
         # Obtiene todas las pistas de bowling ordenadas por su ID.
        return PistaBowling.objects.all().order_by('id_pista')

class EditarPistaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PistaBowling
    template_name = 'editar_pista.html'
    fields = ['capacidad_maxima', 'descripcion', 'estado']
    success_url = reverse_lazy('ver_pistas')

    def test_func(self):
        return self.request.user.is_superuser