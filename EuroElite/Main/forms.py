from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Cita, BloqueHorario

Usuario = get_user_model()


class PerfilForm(forms.ModelForm):
    """Formulario para que el usuario edite su perfil básico."""
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefono']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ========== FORMULARIO DE REGISTRO ==========
class RegistroForm(UserCreationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tu nombre de usuario'})
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'placeholder': 'Ingresa tu correo'})
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingresa tu contraseña'})
    )
    password2 = forms.CharField(
        label="Repetir contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite tu contraseña'})
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']


# ========== FORMULARIO DE AGENDA ==========
class CitaForm(forms.ModelForm):
    """
    Permite al usuario reservar una cita en un bloque de horario disponible.
    """

    # Generamos la lista de bloques disponibles en el momento de mostrar el formulario
    bloque = forms.ModelChoiceField(
        queryset=BloqueHorario.objects.filter(bloqueado=False).order_by('inicio'),
        label="Bloque de horario",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Cita
        fields = ['servicio', 'bloque', 'a_domicilio', 'direccion_domicilio']
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'a_domicilio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'direccion_domicilio': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        bloque = cleaned_data.get("bloque")

        # Validación: impedir reservar un bloque pasado
        if bloque and bloque.inicio <= timezone.now():
            raise forms.ValidationError("No puedes agendar en un bloque de tiempo pasado.")

        return cleaned_data
