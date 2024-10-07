from django import forms
from .models import Cliente
from django.contrib.auth.hashers import make_password  

class ClienteForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Cliente
        fields = ['nombre', 'direccion', 'telefono', 'email', 'password']  
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'Av. Colon 9999'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder' : '+54 9 351 111 1234'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}), 
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])  
        if commit:
            user.save()
        return user


from django.contrib.auth.forms import AuthenticationForm



class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))