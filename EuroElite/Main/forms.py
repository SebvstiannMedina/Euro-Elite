from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cita
import datetime
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
        model = User
        fields = ['username', 'email', 'password1', 'password2']



# ========== FORMULARIO DE AGENDA ==========

def generar_horarios():
    """Genera intervalos de 30 min desde 10:00 hasta 17:00."""
    horas = []
    inicio = datetime.time(10, 0)
    fin = datetime.time(17, 0)
    actual = datetime.datetime.combine(datetime.date.today(), inicio)

    while actual.time() <= fin:
        horas.append((actual.time().strftime("%H:%M"), actual.time().strftime("%H:%M")))
        actual += datetime.timedelta(minutes=30)
    return horas

class CitaForm(forms.ModelForm):
    hora = forms.ChoiceField(choices=generar_horarios(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Cita
        fields = ['servicio', 'fecha', 'hora', 'descripcion']
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': datetime.date.today().strftime("%Y-%m-%d")  # evita fechas pasadas
                }
            ),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    # 🔹 Validación extra para evitar horas pasadas si la fecha es hoy
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha")
        hora_str = cleaned_data.get("hora")

        if fecha and hora_str:
            hora = datetime.datetime.strptime(hora_str, "%H:%M").time()

            # Si la fecha es hoy, verificar que la hora no sea pasada
            if fecha == datetime.date.today() and hora <= datetime.datetime.now().time():
                raise forms.ValidationError("No puedes agendar en una hora pasada.")

        return cleaned_data