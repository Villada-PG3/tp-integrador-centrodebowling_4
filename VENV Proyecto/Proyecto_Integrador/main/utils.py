from datetime import timedelta
from .models import Reserva, PistaBowling, HistorialEstado, EstadoReserva

def comprobar_disponibilidad_pistas(fecha_hora_reserva, pista):
    # Verificar si la pista está en estado 'Disponible'
    if pista.estado.estado != 'Disponible':
        return False
    
    # Verificar si hay reservas confirmadas en el rango de tiempo
    reservas = Reserva.objects.filter(
        fecha_hora_reserva__lte=fecha_hora_reserva + timedelta(hours=2),
        fecha_hora_reserva__gte=fecha_hora_reserva ,
        id_pista=pista
    )
    
    # Comprobar si alguna reserva tiene estado 'Confirmada'
    for reserva in reservas:
        if HistorialEstado.objects.filter(id_reserva=reserva, estado__estado='Confirmada').exists():
            return False
        elif HistorialEstado.objects.filter(id_reserva=reserva, estado__estado='En curso').exists():
            return False
    
    return True