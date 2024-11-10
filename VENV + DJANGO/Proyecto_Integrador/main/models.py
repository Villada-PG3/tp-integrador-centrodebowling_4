from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta

class ClienteManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener una dirección de correo electrónico.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Cliente(AbstractBaseUser, PermissionsMixin):
    id_cliente = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=60)
    direccion = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = ClienteManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return f"Email: {self.email} - Nombre: {self.nombre}"

class PistaBowling(models.Model):
    id_pista = models.AutoField(primary_key=True)
    capacidad_maxima = models.IntegerField()
    descripcion = models.CharField(max_length=240)
    estado = models.ForeignKey("EstadoPista", on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.descripcion)

class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)  
    id_pista = models.ForeignKey(PistaBowling, on_delete=models.CASCADE, default=1) 
    fecha_hora_reserva = models.DateTimeField()
    fecha_hora_fin = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"ID: {self.id_reserva} - {self.id_cliente} - Id Pista:{self.id_pista}"
    
    def get_reserva_x_cliente(self, cliente):
        return Reserva.objects.filter(id_cliente = cliente)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.crear_historial_estado_inicial()

    def crear_historial_estado_inicial(self):
        estado_confirmada = EstadoReserva.objects.get(estado='Confirmada')
        if not HistorialEstado.objects.filter(id_reserva=self, estado=estado_confirmada).exists():
            HistorialEstado.objects.create(
                id_reserva=self, 
                estado=estado_confirmada, 
                fecha_hora_inicio=timezone.now(),
                fecha_hora_fin=self.fecha_hora_reserva
            )

    def procesar_reserva(self):
        self.actualizar_ultimo_estado()
        self.verificar_confirmacion()
        self.verificar_estado_actual()
        self.verificar_finalizacion()
        self.actualizar_fecha_hora_fin()

    def actualizar_ultimo_estado(self):
        try:
            self.ultimo_estado = self.historialestado_set.latest('fecha_hora_inicio')
        except HistorialEstado.DoesNotExist:
            self.ultimo_estado = None

    def verificar_confirmacion(self):
        estado_default = EstadoReserva.objects.get(estado='Confirmada')
        if not HistorialEstado.objects.filter(id_reserva=self, estado=estado_default).exists():
            self.crear_historial_estado(estado_default, timezone.now(), timezone.now() + timedelta(hours=2))

    def verificar_estado_actual(self):
        ahora = timezone.now()
        if self.fecha_hora_reserva and self.fecha_hora_reserva <= ahora:
            estado_en_curso = EstadoReserva.objects.get(estado='En Curso')
            if self.ultimo_estado.estado.estado == 'Confirmada':
                self.crear_historial_estado(estado_en_curso, ahora, ahora + timedelta(hours=2))

    def verificar_finalizacion(self):
        ahora = timezone.now()
        if self.fecha_hora_fin and self.fecha_hora_reserva <= ahora and self.fecha_hora_fin <= ahora.time():
            estado_finalizada = EstadoReserva.objects.get(estado='Finalizada')
            if self.ultimo_estado.estado.estado == 'En Curso':
                self.crear_historial_estado(estado_finalizada, ahora, ahora)

    def actualizar_fecha_hora_fin(self):
        if self.fecha_hora_reserva:
            hora_final = self.fecha_hora_reserva + timedelta(hours=2)
            self.fecha_hora_fin = hora_final.time()
            self.save()

    def crear_historial_estado(self, estado, fecha_inicio, fecha_fin):
        if HistorialEstado.objects.filter(id_reserva=self, estado=estado).exists():
            HistorialEstado.objects.filter(id_reserva=self, estado=estado).delete()
        HistorialEstado.objects.create(
            id_reserva=self,
            estado=estado,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin
        )

    def finalizar(self):
        estado_finalizada = EstadoReserva.objects.get(estado='Finalizada')
        self.crear_historial_estado(estado_finalizada, timezone.now(), timezone.now())
        self.estado = estado_finalizada
        self.save()

    @property
    def estado_actual(self):
        try:
            return self.historialestado_set.latest('fecha_hora_inicio').estado.estado
        except HistorialEstado.DoesNotExist:
            return 'Confirmada'

class EstadoReserva(models.Model):
    estado = models.CharField(max_length=20, primary_key=True)
    descripcion = models.CharField(max_length=240)

    def __str__(self):
        return self.estado

class Jugador(models.Model):
    id_jugador = models.AutoField(primary_key=True)
    id_partida = models.ForeignKey('Partida', on_delete=models.CASCADE, default=1) 
    nombre_jugador = models.CharField(max_length=10)
    orden = models.IntegerField()

    def __str__(self):
        return str(self.id_jugador)

    @property
    def puntaje_total(self):
        return sum(tirada.pinos_deribados for tirada in self.tirada_set.all())

class Partida(models.Model):
    id_partida = models.AutoField(primary_key=True)
    id_pista = models.ForeignKey(PistaBowling, on_delete=models.CASCADE, default=1)
    id_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, default=1)
    estado = models.ForeignKey('EstadoPartida', on_delete=models.CASCADE, default='Disponible')
    cant_jugadores = models.IntegerField(null=True, blank=True)
    ganador = models.ForeignKey(Jugador, on_delete=models.SET_NULL, null=True, blank=True, related_name='partidas_ganadas')

    def __str__(self):
        return str(f"{self.id_partida} - {self.estado}")

    

    @classmethod
    def crear_partidas_para_reserva(cls, reserva):
        partidas = list(cls.objects.filter(id_reserva=reserva).order_by('id_partida'))
        
        # Si hay menos de 3 partidas, se crean las necesarias
        if len(partidas) < 3:
            estado_disponible = EstadoPartida.objects.get(estado='Disponible')
            estado_bloqueado = EstadoPartida.objects.get(estado='Bloqueada')

            for i in range(3 - len(partidas)):
                # La primera partida creada debe estar disponible
                if i == 0:
                    estado_partida = estado_disponible
                else:
                    estado_partida = estado_bloqueado
                
                nueva_partida = cls.objects.create(
                    id_pista=reserva.id_pista,
                    id_reserva=reserva,
                    estado=estado_partida,
                    cant_jugadores=0
                )
                partidas.append(nueva_partida)

        return partidas

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

    def get_current_turn(self):
        turnos = self.turno_set.order_by('numero_turno')
        tiradas = Tirada.objects.filter(numero_turno__in=turnos)
        tiradas_count = tiradas.count()
        jugadores_count = self.jugador_set.count()
        
        current_turn_index = tiradas_count // (2 * jugadores_count)
        if current_turn_index < turnos.count():
            return turnos[current_turn_index]
        else:
            return turnos.last()

    def is_game_finished(self):
        turnos = self.turno_set.all()
        jugadores = self.jugador_set.all()
        tiradas = Tirada.objects.filter(numero_turno__in=turnos)

        expected_tiradas = sum(3 if turno.ultimo_turno else 2 for turno in turnos) * jugadores.count()
        return tiradas.count() >= expected_tiradas

    def finalize_game(self, partida):
        self.set_partida_winner(partida)
        self.estado = EstadoPartida.objects.get(estado='Finalizada')
        self.save()

    def crear_turnos(self):
        for i in range(1, 11):
            Turno.objects.create(
                id_partida=self,
                orden=i,
                ultimo_turno=(i == 10)
            )

    def iniciar_partida(self):
        estado_en_proceso = EstadoPartida.objects.get(estado='En proceso')
        self.estado = estado_en_proceso
        self.save()

class EstadoPartida(models.Model):
    estado = models.CharField(max_length=20, primary_key=True)
    descripcion = models.CharField(max_length=240)

    def __str__(self):
        return self.estado

class Turno(models.Model):
    numero_turno = models.AutoField(primary_key=True)
    id_partida = models.ForeignKey(Partida, on_delete=models.CASCADE, default=1)
    orden = models.CharField(max_length=20)
    ultimo_turno = models.BooleanField()

    def __str__(self):
        return str(self.numero_turno)

class Tirada(models.Model):
    numero_tirada = models.AutoField(primary_key=True)
    pinos_deribados = models.IntegerField()
    orden = models.IntegerField()
    id_jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, default=1)
    numero_turno = models.ForeignKey(Turno, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.numero_tirada)

    @classmethod
    def registrar_tirada(cls, jugador, turno, pinos_derribados, orden):
        return cls.objects.create(
            pinos_deribados=pinos_derribados,
            orden=orden,
            id_jugador=jugador,
            numero_turno=turno,
        )

class EstadoPista(models.Model):
    estado = models.CharField(max_length=20, primary_key=True)
    descripcion = models.CharField(max_length=240)

    def __str__(self):
        return self.estado

class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    estado = models.ForeignKey('EstadoPedido', on_delete=models.CASCADE, default='PENDIENTE')
    fecha_hora_pedido = models.DateField()
    id_reserva = models.ForeignKey('Reserva',on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(f"ID: {self.id_pedido} - Estado: {self.estado}")

    def obtener_pedidos_reserva(self, reserva):
        return Pedido.objects.filter(id_reserva=reserva)
    @property
    def total_a_pagar(self):
        return sum(item.cantidad * item.id_producto.precio for item in self.pedidoxproducto_set.all())

    @classmethod
    def crear_pedido(cls, reserva, productos, cantidades):
        pedido = cls.objects.create(
            id_reserva=reserva,
            fecha_hora_pedido=timezone.now(),
            estado=EstadoPedido.objects.get(estado='Pedido Confirmado')
        )

        for producto_id, cantidad in zip(productos, cantidades):
            PedidoXProducto.objects.create(
                id_pedido=pedido,
                id_producto_id=producto_id,
                cantidad=int(cantidad)
            )

        return pedido

class EstadoPedido(models.Model):
    estado = models.CharField(max_length=20, primary_key=True)
    descripcion = models.CharField(max_length=240)

    def __str__(self):
        return self.estado

class PedidoXProducto(models.Model):
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, default=1) 
    id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE, default=1) 
    cantidad = models.IntegerField()

    class Meta:
        unique_together = ('id_pedido', 'id_producto')

    def __str__(self):
        return f'{self.id_pedido}-{self.id_producto}'

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    descripcion = models.CharField(max_length=240)
    precio = models.IntegerField()

    def __str__(self):
        return str(f"{self.id_producto} - {self.nombre}")

class HistorialEstado(models.Model):
    id_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, default=1)  
    estado = models.ForeignKey(EstadoReserva, on_delete=models.CASCADE, default='PENDIENTE')
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()

    class Meta:
        unique_together = ('id_reserva', 'estado')

    def __str__(self):
        return f'{self.id_reserva}-{self.estado}'