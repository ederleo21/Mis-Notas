from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.urls import reverse_lazy
from django import forms


class RegisterForm(UserCreationForm):
    """Formulario de registro con nombre y apellido."""
    first_name = forms.CharField(
        max_length=100, required=True, label='Nombres',
        widget=forms.TextInput(attrs={'placeholder': 'Ej: María Elena'})
    )
    last_name = forms.CharField(
        max_length=100, required=True, label='Apellidos',
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Jerez Cárdenas'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Ej: mjerez'
        self.fields['password1'].widget.attrs['placeholder'] = '••••••••'
        self.fields['password2'].widget.attrs['placeholder'] = '••••••••'


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Auto-login después del registro
        login(self.request, self.object)
        return response
