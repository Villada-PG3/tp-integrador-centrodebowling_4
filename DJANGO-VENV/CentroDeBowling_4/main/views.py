from django.shortcuts import render

from django.shortcuts import render



from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import ClienteForm, CustomLoginForm
from django.views.generic import ListView
from .models import Cliente
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse

class IndexView(TemplateView):
    template_name = 'index.html'
    

class ClienteCreateView(FormView):
    template_name = 'cliente_form.html'
    form_class = ClienteForm
    success_url = reverse_lazy('cliente_success')

    def form_valid(self, form):
        form.save()  
        return super().form_valid(form)
    
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomLoginForm
    
def custom_logout_view(request):
    logout(request)
    return redirect(reverse('index'))
    

    
class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'cliente_list.html'
    context_object_name = 'clientes'




