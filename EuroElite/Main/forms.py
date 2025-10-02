from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone

from .models import Cita, BloqueHorario, Servicio, Producto, Direccion

Usuario = get_user_model()


# ================= PERFIL =================
class PerfilForm(forms.ModelForm):
    """Formulario para que el usuario edite su perfil básico."""
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefono', 'rut']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ================= REGISTRO =================
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


# ================= CITA =================
class CitaForm(forms.ModelForm):
    bloque = forms.ModelChoiceField(
        queryset=BloqueHorario.objects.filter(
            bloqueado=False, inicio__gte=timezone.now()
        ).order_by('inicio'),
        label="Bloque de horario",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True),
        label="Servicio requerido",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Cita
        fields = ['servicio', 'bloque', 'a_domicilio', 'direccion_domicilio']
        widgets = {
            'a_domicilio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'direccion_domicilio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Av. Libertador 1234, Santiago'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        bloque = cleaned_data.get("bloque")

  
        if bloque and bloque.inicio <= timezone.now():
            raise forms.ValidationError("No puedes agendar en un bloque de tiempo pasado.")


        if bloque and hasattr(bloque, "cita"):
            raise forms.ValidationError("Este bloque ya está reservado.")


        a_domicilio = cleaned_data.get("a_domicilio")
        direccion = cleaned_data.get("direccion_domicilio")
        if a_domicilio and not direccion:
            self.add_error("direccion_domicilio", "Debes ingresar una dirección para el servicio a domicilio.")

        return cleaned_data


# ================= PRODUCTO =================
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'sku', 'marca', 'descripcion',
            'precio', 'costo', 'stock', 'stock_minimo',
            'activo', 'categoria', 'imagen',
            
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }


# ================= DIRECCION =================
class DireccionForm(forms.ModelForm):
    """Formulario para editar o agregar dirección del usuario."""
    class Meta:
        model = Direccion
        fields = ['linea1', 'linea2', 'comuna', 'ciudad', 'region', 'codigo_postal']
        widgets = {
            'linea1': forms.TextInput(attrs={'class': 'form-control'}),
            'linea2': forms.TextInput(attrs={'class': 'form-control'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={"class": "form-control"}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
        }

# ================= Login Con correo =================

class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'placeholder': 'Ingresa tu correo', 'class': 'form-control'})
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingresa tu contraseña', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            try:
                user = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                raise forms.ValidationError("Correo o contraseña incorrectos.")
            
            user = authenticate(username=user.username, password=password)
            if user is None:
                raise forms.ValidationError("Correo o contraseña incorrectos.")
            
            self.user_cache = user
        return cleaned_data
    
    def get_user(self):
        return getattr(self, "user_cache", None)
