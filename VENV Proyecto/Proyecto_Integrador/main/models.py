from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Manager para el modelo Cliente
class ClienteManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # Método para crear un usuario normal
        if not email:
            raise ValueError('El usuario debe tener una dirección de correo electrónico.')
        email = self.normalize_email(email)  # Normaliza el correo electrónico
        user = self.model(email=email, **extra_fields)  # Crea el objeto usuario
        user.set_password(password)  # Establece la contraseña
        user.save(using=self._db)  # Guarda el usuario en la base de datos
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        # Método para crear un superusuario
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Modelo Cliente
class Cliente(AbstractBaseUser, PermissionsMixin):
    id_cliente = models.AutoField(primary_key=True)  # ID del cliente (clave primaria)
    email = models.EmailField(unique=True, default='default@example.com')  # Correo electrónico único
    nombre = models.CharField(max_length=60)  # Nombre del cliente
    direccion = models.CharField(max_length=120)  # Dirección del cliente
    telefono = models.CharField(max_length=20)  # Teléfono del cliente
    password = models.CharField(max_length=128)  # Contraseña (almacenada como hash)

    is_staff = models.BooleanField(default=False)  # Indica si el usuario es un miembro del personal
    is_active = models.BooleanField(default=True)  # Indica si el usuario está activo
    is_superuser = models.BooleanField(default=False)  # Indica si el usuario es un superusuario

    objects = ClienteManager()  # Asigna el manager personalizado

    USERNAME_FIELD = 'email'  # Campo que se usará para el inicio de sesión
    REQUIRED_FIELDS = ['nombre']  # Campos requeridos para crear un usuario

    def __str__(self):
        return self.email  # Representación en cadena del cliente


# Modelo PistaBowling
class PistaBowling(models.Model):
    id_pista = models.AutoField(primary_key=True)  # ID de la pista (clave primaria)
    capacidad_maxima = models.IntegerField()  # Capacidad máxima de la pista
    descripcion = models.CharField(max_length=240)  # Descripción de la pista
    estado = models.ForeignKey("EstadoPista", on_delete=models.CASCADE, default=1)  # Estado de la pista (FK)

    def __str__(self):
        return str(self.descripcion)  # Representación en cadena de la pista


from django.utils import timezone

# Modelo Reserva
class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)  # ID de la reserva (clave primaria)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)  # Cliente que realizó la reserva (FK)
    id_pista = models.ForeignKey(PistaBowling, on_delete=models.CASCADE, default=1)  # Pista reservada (FK)
    fecha_hora_reserva = models.DateTimeField()  # Fecha y hora de la reserva
    fecha_hora_fin = models.TimeField(null=True, blank=True)  # Fecha y hora de finalización de la reserva

    def __str__(self):
        return str(self.id_reserva)  # Representación en cadena de la reserva

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guarda la reserva
        estado_confirmada = EstadoReserva.objects.get(estado='Confirmada')  # Obtiene el estado 'Confirmada'
        # Crea un historial de estado si no existe
        if not HistorialEstado.objects.filter(id_reserva=self, estado=estado_confirmada).exists():
            HistorialEstado.objects.create(
                id_reserva=self, 
                estado=estado_confirmada, 
                fecha_hora_inicio=timezone.now(),
                fecha_hora_fin=self.fecha_hora_reserva
            )


# Modelo EstadoReserva
class EstadoReserva(models.Model):
    estado = models.CharField(max_length=20, primary_key=True)  # Estado de la reserva (clave primaria)
    descripcion = models.CharField(max_length=240)  # Descripción del estado

    def __str__(self):
        return self.estado  # Representación en cadena del estado de reserva


# Modelo Jugador
class Jugador(models.Model):
    id_jugador = models.AutoField(primary_key=True)  # ID del jugador (clave primaria)
    id_partida = models.ForeignKey('Partida', on_delete=models.CASCADE, default=1)  # Partida asociada (FK)
    nombre_jugador = models.CharField(max_length=10)  # Nombre del jugador
    orden = models.IntegerField()  # Orden en la partida

    def __str__(self):
        return str(self.id_jugador)  # Representación en cadena del jugador


# Modelo Partida
class Partida(models.Model):
    id_partida = models.AutoField(primary_key=True)  # ID de la partida (clave primaria)
    id_pista = models.ForeignKey(PistaBowling, on_delete=models.CASCADE, default=1)  # Pista asociada (FK)
    id_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, default=1)  # Reserva asociada (FK)
    estado = models.ForeignKey('EstadoPartida', on_delete=models.CASCADE, default='Disponible')  # Estado de la partida (FK)
    cant_jugadores = models.IntegerField(null=True, blank=True)  # Cantidad de jugadores en la partida

    def __str__(self):
        return str(f"{self.id_partida} - {self.estado}")  # Representación en cadena de la partida

    def actualizar_estado(self):
        # Método para actualizar el estado de la partida
        if self.estado.estado == 'Finalizada':
            # Lógica para habilitar la siguiente partida
            partidas = Partida.objects.filter(id_reserva=self.id_reserva)
            if partidas.filter(estado__estado='Finalizada').count() == 2:
                siguiente_partida = partidas.exclude(id_partida=self.id_partida).filter(estado__estado='Bloqueada').first()
                if siguiente_partida:
                    siguiente_partida.estado = EstadoPartida.objects.get(estado='Disponible')  # Cambia el estado a 'Disponible'
                    siguiente_partida.save()  # Guarda los cambios en la partida


# Modelo EstadoPartida
class EstadoPartida(models.Model):
    estado = models.CharField(max_length=20, primary_key=True)  # Estado de la partida (clave primaria)
    descripcion = models.CharField(max_length=240)  # Descripción del estado

    def __str__(self):
        return self.estado  # Representación en cadena del estado de la partida


# Modelo Turno
class Turno(models.Model):
    numero_turno = models.AutoField(primary_key=True)  # ID del turno (clave primaria)
    id_partida = models.ForeignKey(Partida, on_delete=models.CASCADE, default=1)  # Partida asociada (FK)
    orden = models.CharField(max_length=20)  # Orden del turno
    ultimo_turno = models.BooleanField()  # Indica si es el último turno

    def __str__(self):
        return str(self.numero_turno)  # Representación en cadena del turno


# Modelo Tirada
class Tirada(models.Model):
    numero_tirada = models.AutoField(primary_key=True)  # ID de la tirada (clave primaria)
    pinos_deribados = models.IntegerField()  # Número de pinos derribados
    orden = models.IntegerField()  # Orden de la tirada
    id_jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, default=1)  # Jugador que realizó la tirada (FK)
    numero_turno = models.ForeignKey(Turno, on_delete=models.CASCADE, default=1)  # Turno de la tirada (FK)

    def __str__(self):
        return str(self.numero_tirada)  # Representación en cadena de la tirada


# Modelo EstadoPista
class EstadoPista(models.Model):
    estado = models.CharField(max_length=20, primary_key=True)  # Estado de la pista (clave primaria)
    descripcion = models.CharField(max_length=240)  # Descripción del estado

    def __str__(self):
        return self.estado  # Representación en cadena del estado de la pista


# Modelo Pedido
class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)  # ID del pedido (clave primaria)
    
    estado = models.ForeignKey('EstadoPedido', on_delete=models.CASCADE, default='PENDIENTE')  # Estado del pedido (FK)
    fecha_hora_pedido = models.DateField()  # Fecha y hora del pedido
    id_reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE, default=1)  # Reserva
