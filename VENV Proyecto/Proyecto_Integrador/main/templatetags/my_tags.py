from django import template
from ..models import Reserva
from datetime import timedelta

register = template.Library()

@register.filter
def comprobar_disponibilidad_pistas(pista, fecha_hora_reserva):
    if pista is None:
        return False
    fecha_hora_reserva_fin = fecha_hora_reserva + timedelta(hours=2)
    reservas = Reserva.objects.filter(id_pista=pista.choice_value, fecha_hora_reserva__gte = fecha_hora_reserva, fecha_hora_reserva__lte=fecha_hora_reserva_fin)
    return not reservas.exists()







