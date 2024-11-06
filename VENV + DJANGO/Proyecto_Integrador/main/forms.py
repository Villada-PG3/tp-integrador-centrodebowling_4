
from django.forms import inlineformset_factory
from django import forms
from .models import Cliente
from django.contrib.auth.hashers import make_password 
from .utils import comprobar_disponibilidad_pistas 

from django import forms
from .models import Reserva, EstadoReserva, PistaBowling

from django import forms
from .models import Reserva, PistaBowling
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django import forms

from django import forms
from .models import Pedido, Producto, PedidoXProducto

from django import forms
from .models import Pedido, Producto

from django import forms
from .models import Producto



class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))


class CustomRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Cliente
        fields = ['nombre', 'direccion', 'telefono', 'email', 'password']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Av. Colon 9999'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+54 9 351 111 1234'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@example.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
    


class ReservaForm(forms.ModelForm):
    fecha_hora_reserva = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class':"form-control" }, format='%Y-%m-%dT%H:%M'),
        input_formats=('%Y-%m-%dT%H:%M',)
    )
    id_pista = forms.ModelChoiceField(
        queryset=PistaBowling.objects.all(),
        widget=forms.RadioSelect(attrs={'class': 'lineas'}),
        empty_label=None
    )

    email_cliente = forms.EmailField(label='Correo electrónico: ', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese correo'}))

    class Meta:
        model = Reserva
        fields = ['fecha_hora_reserva', 'id_pista', 'email_cliente']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ReservaForm, self).__init__(*args, **kwargs)
        
    def clean_id_pista(self):
        fecha_hora_reserva = self.cleaned_data['fecha_hora_reserva']
        pista = self.cleaned_data['id_pista']  # Obtener el objeto PistaBowling

        # Verificar si la pista está disponible en la fecha y hora seleccionada
        if not comprobar_disponibilidad_pistas(fecha_hora_reserva, pista):
            raise forms.ValidationError('La pista no está disponible en la fecha y hora seleccionada')

        return pista

    def clean_email_cliente(self):
        
        email_cliente = self.cleaned_data['email_cliente']
        if email_cliente != self.request.user.email:
            raise forms.ValidationError('El correo electrónico debe ser el mismo que el de su cuenta')
        else:
            try:
                cliente = Cliente.objects.get(email=email_cliente)
                return cliente
            except Cliente.DoesNotExist:
                raise forms.ValidationError('El correo electrónico del cliente no existe')




class JugadoresForm(forms.Form):
    cantidad_jugadores = forms.IntegerField(
        label='Cantidad de Jugadores',
        min_value=2,
        max_value=10,  # Cambia el valor máximo según la capacidad máxima de la pista
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    
    


class MultiplePedidoForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Producto.objects.all(), label='Producto')
    cantidad = forms.IntegerField(min_value=1, required=True, label='Cantidad')




class ReservaEditForm(forms.ModelForm):
    nuevo_estado = forms.ModelChoiceField(
        queryset=EstadoReserva.objects.all(),
        required=False,
        label="Nuevo Estado"
    )
    
    class Meta:
        model = Reserva
        fields = ['id_cliente', 'id_pista', 'fecha_hora_reserva', 'fecha_hora_fin']
        widgets = {
            'fecha_hora_reserva': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_pista'].queryset = PistaBowling.objects.all()


from django import forms
from .models import Pedido, PedidoXProducto, EstadoPedido, Producto

