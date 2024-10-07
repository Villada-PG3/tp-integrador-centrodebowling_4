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

    

class Cliente(AbstractBaseUser, PermissionsMixin):
    id_cliente = models.AutoField(primary_key=True)  # Clave primaria auto incremental
    email = models.EmailField(unique=True,  default='default@example.com') # le pomgo que sea unique al mail para que sirva para iniciar sesion, seria como 
                                                                            # otra PK aparete del ID
    nombre = models.CharField(max_length=60)
    direccion = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20)
    password = models.CharField(max_length=128)   # Valor predeterminado temporal
    

    objects = ClienteManager()
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.email



class PistaBowling(models.Model):
    id_pista = models.AutoField(primary_key=True)
    capacidad_maxima = models.IntegerField()
    descripcion = models.CharField(max_length=240)
    estado = models.ForeignKey('EstadoPista', on_delete=models.CASCADE, default='DISPONIBLE')

    def __str__(self):
        return str(self.id_pista)


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)  
    id_pista = models.ForeignKey(PistaBowling, on_delete=models.CASCADE, default=1) 
    fecha_hora_reserva = models.DateField()
    id_partida = models.ForeignKey('Partida', on_delete=models.CASCADE, default=1)  
    id_pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, default=1)  
    estado = models.CharField(max_length=20)

    def __str__(self):
        return str(self.id_reserva)


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
    estado = models.ForeignKey('EstadoPartida', on_delete=models.CASCADE, default='INICIADA')

    def __str__(self):
        return str(self.id_partida)


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
    id_producto = models.ForeignKey('Producto', on_delete=models.CASCADE, default=1)  
    estado = models.ForeignKey('EstadoPedido', on_delete=models.CASCADE, default='PENDIENTE')
    fecha_hora_pedido = models.DateField()

    def __str__(self):
        return str(self.id_pedido)


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
        return str(self.id_producto)


class HistorialEstado(models.Model):
    id_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, default=1)  
    estado = models.ForeignKey(EstadoReserva, on_delete=models.CASCADE, default='PENDIENTE')
    fecha_hora_inicio = models.DateField()
    fecha_hora_fin = models.DateField()

    class Meta:
        unique_together = ('id_reserva', 'estado')

    def __str__(self):
        return f'{self.id_reserva}-{self.estado}'
