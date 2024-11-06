from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin





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
    is_superuser = models.BooleanField(default=False)  # Add this line

    objects = ClienteManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return (f"Email: {self.email} - Nombre: {self.nombre}")



class PistaBowling(models.Model):
    id_pista = models.AutoField(primary_key=True)
    capacidad_maxima = models.IntegerField()
    descripcion = models.CharField(max_length=240)
    estado = models.ForeignKey("EstadoPista", on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.descripcion)


from django.utils import timezone

class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)  
    id_pista = models.ForeignKey(PistaBowling, on_delete=models.CASCADE, default=1) 
    fecha_hora_reserva = models.DateTimeField()
    fecha_hora_fin = models.TimeField(null=True, blank=True)
    
    

    def __str__(self):
        return (f"ID: {self.id_reserva} - {self.id_cliente} - Id Pista:{self.id_pista}")
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        estado_confirmada = EstadoReserva.objects.get(estado='Confirmada')
        if not HistorialEstado.objects.filter(id_reserva=self, estado=estado_confirmada).exists():
            HistorialEstado.objects.create(
                id_reserva=self, 
                estado=estado_confirmada, 
                fecha_hora_inicio=timezone.now(),
                fecha_hora_fin=self.fecha_hora_reserva
            )

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

class Partida(models.Model):
    id_partida = models.AutoField(primary_key=True)
    id_pista = models.ForeignKey(PistaBowling, on_delete=models.CASCADE, default=1)  
    id_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, default=1)  
    estado = models.ForeignKey('EstadoPartida', on_delete=models.CASCADE, default='Disponible')
    cant_jugadores = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(f"{self.id_partida} - {self.estado}")

    def actualizar_estado(self):
        if self.estado.estado == 'Finalizada':
            # Lógica para habilitar la siguiente partida
            partidas = Partida.objects.filter(id_reserva=self.id_reserva)
            if partidas.filter(estado__estado='Finalizada').count() == 2:
                siguiente_partida = partidas.exclude(id_partida=self.id_partida).filter(estado__estado='Bloqueada').first()
                if siguiente_partida:
                    siguiente_partida.estado = EstadoPartida.objects.get(estado='Disponible')
                    siguiente_partida.save()

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
