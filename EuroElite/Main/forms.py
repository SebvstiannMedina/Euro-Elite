from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone

from .models import Cita, BloqueHorario, Servicio, Producto, Direccion, Promocion

Usuario = get_user_model()


# ================= PERFIL =================
class PerfilForm(forms.ModelForm):
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        telefono_digits = ''.join(filter(str.isdigit, telefono))
        if len(telefono_digits) != 8:
            raise forms.ValidationError('El teléfono debe tener exactamente 8 dígitos.')
        return telefono_digits
    
    def clean_first_name(self):
        first = (self.cleaned_data.get('first_name', '') or '').strip()
        if any(ch.isdigit() for ch in first):
            raise forms.ValidationError('El nombre no puede contener números.')
        if len(first) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if len(first) > 25:
            raise forms.ValidationError('El nombre no puede tener más de 25 caracteres.')
        return first
    def clean_last_name(self):
        last = (self.cleaned_data.get('last_name', '') or '').strip()
        if any(ch.isdigit() for ch in last):
            raise forms.ValidationError('El apellido no puede contener números.')
        if len(last) < 3:
            raise forms.ValidationError('El apellido debe tener al menos 3 caracteres.')
        if len(last) > 25:
            raise forms.ValidationError('El apellido no puede tener más de 25 caracteres.')
        return last

    def clean_email(self):
        email = (self.cleaned_data.get('email', '') or '').strip()
        if not email:
            raise forms.ValidationError('El correo electrónico es obligatorio.')
        if len(email) < 5:
            raise forms.ValidationError('El correo electrónico debe tener al menos 5 caracteres.')
        if len(email) > 100:
            raise forms.ValidationError('El correo electrónico no puede tener más de 100 caracteres.')
        email = ''.join(ch for ch in email if ch not in '\r\n\t')
        return email

    """Formulario para que el usuario edite su perfil básico."""
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'rut']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'oninput': "this.value=this.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]/g,'');",
                'minlength': '3',
                'maxlength': '25'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'oninput': "this.value=this.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]/g,'');",
                'minlength': '3',
                'maxlength': '25'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'required': True,
                'minlength': '5',
                'maxlength': '100',
                'oninput': "this.value=this.value.trim().replace(/[\r\n\t]/g,'')"
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'oninput': "this.value=this.value.replace(/[^0-9]/g,'');",
                'maxlength': '8'
            }),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ================= REGISTRO =================
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroForm(UserCreationForm):

    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'placeholder': 'Ingresa tu correo', 'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingresa tu contraseña', 'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Repetir contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite tu contraseña', 'class': 'form-control'})
    )
    first_name = forms.CharField(
        label="Nombre", 
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingresa tu nombre',
            'class': 'form-control',
            'oninput': "this.value=this.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]/g,'');",
            'minlength': '3',
            'maxlength': '25'
        })
    )
    last_name = forms.CharField(
        label="Apellido", 
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingresa tu apellido',
            'class': 'form-control',
            'oninput': "this.value=this.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]/g,'');",
            'minlength': '3',
            'maxlength': '25'
        })
    )

    def clean_first_name(self):
        first = (self.cleaned_data.get('first_name', '') or '').strip()
        if any(ch.isdigit() for ch in first):
            raise forms.ValidationError('El nombre no puede contener números.')
        if len(first) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if len(first) > 25:
            raise forms.ValidationError('El nombre no puede tener más de 25 caracteres.')
        return first

    def clean_last_name(self):
        last = (self.cleaned_data.get('last_name', '') or '').strip()
        if any(ch.isdigit() for ch in last):
            raise forms.ValidationError('El apellido no puede contener números.')
        if len(last) < 3:
            raise forms.ValidationError('El apellido debe tener al menos 3 caracteres.')
        if len(last) > 25:
            raise forms.ValidationError('El apellido no puede tener más de 25 caracteres.')
        return last
    telefono = forms.CharField(
        label="Teléfono", 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tu teléfono', 'class': 'form-control'})
    )
    accept_legal_terms = forms.BooleanField(
        label="Acepto los términos",
        required=True
    )

    class Meta:
        model = Usuario
        fields = [
            'email', 'first_name', 'last_name',
            'telefono', 'password1', 'password2', 'accept_legal_terms'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.telefono = self.cleaned_data['telefono']
        user.accept_legal_terms = self.cleaned_data['accept_legal_terms']

        # 👇 se cifra la contraseña correctamente
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user


# ================= CITA =================
class CitaForm(forms.ModelForm):
    # Campo de selección del bloque horario (el queryset se define en __init__)
    bloque = forms.ModelChoiceField(
        queryset=BloqueHorario.objects.none(),
        label="Bloque de horario",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Servicio (solo los activos)
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True),
        label="Servicio requerido",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Cita
        fields = ['servicio', 'bloque', 'a_domicilio', 'direccion_domicilio']
        widgets = {
            'direccion_domicilio': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["bloque"].queryset = (
            BloqueHorario.objects
            .filter(inicio__date__gte=timezone.localdate()) 
            .filter(cita__isnull=True)                
            .order_by("inicio")
        )

    def clean(self):
        cleaned_data = super().clean()
        bloque = cleaned_data.get("bloque")

        if bloque and bloque.inicio <= timezone.now():
            raise forms.ValidationError("No puedes agendar en un bloque de tiempo pasado.")

        if bloque and hasattr(bloque, "cita"):
            raise forms.ValidationError("Este bloque ya está reservado.")

        # Validación para servicio a domicilio
        a_domicilio = cleaned_data.get("a_domicilio")
        direccion = cleaned_data.get("direccion_domicilio")
        if a_domicilio and not direccion:
            self.add_error("direccion_domicilio", "Debes ingresar una dirección para el servicio a domicilio.")



# ================= PRODUCTO =================
class ProductoForm(forms.ModelForm):
    promocion = forms.ModelChoiceField(
        queryset=Promocion.objects.filter(activa=True),
        required=False,
        label="Promoción",
        help_text="Selecciona una promoción o deja vacío si no aplica."
    )

    class Meta:
        model = Producto
        fields = [
            'nombre', 'sku', 'marca', 'descripcion',
            'precio', 'costo', 'stock', 'stock_minimo',
            'activo', 'categoria', 'imagen'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # inicializa con la primera promo asignada si existe
        if self.instance.pk:
            promo = self.instance.promociones.first()
            self.fields['promocion'].initial = promo

    def save(self, commit=True):
        producto = super().save(commit=commit)
        if commit:
            promo = self.cleaned_data.get('promocion')
            if promo:
                producto.promociones.set([promo])  # asignar la promo elegida
            else:
                producto.promociones.clear()  # limpiar si no se seleccionó nada
        return producto


# ================= DIRECCION =================
class DireccionForm(forms.ModelForm):
    """Formulario para editar o agregar dirección del usuario."""
    def clean_codigo_postal(self):
        codigo = self.cleaned_data.get('codigo_postal', '')
        codigo_digits = ''.join(filter(str.isdigit, str(codigo)))
        if len(codigo_digits) != 7:
            raise forms.ValidationError('El código postal debe tener exactamente 7 dígitos.')
        return codigo_digits
    class Meta:
        model = Direccion
        fields = ['linea1', 'linea2', 'comuna', 'region', 'codigo_postal']
        widgets = {
            'linea1': forms.TextInput(attrs={
                'class': 'form-control',
                'oninput': "this.value=this.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 ]/g,'');"
            }),
            'linea2': forms.TextInput(attrs={
                'class': 'form-control',
                'oninput': "this.value=this.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 ]/g,'');"
            }),
            'comuna': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={"class": "form-control"}),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'form-control',
                'oninput': "this.value=this.value.replace(/[^0-9]/g,'');",
                'maxlength': '7',
                'pattern': '[0-9]{7}'
            }),
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
            user = authenticate(username=email, password=password)  # 👈 login con email
            if user is None:
                raise forms.ValidationError("Correo o contraseña incorrectos.")
            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return getattr(self, "user_cache", None)

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            "autofocus": True,
            "class": "form-control",
            "placeholder": "Ingresa tu correo"
        })
    )

from django import forms
from .models import VehiculoEnVenta

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = VehiculoEnVenta
        fields = [
            'marca', 'modelo', 'año', 'kilometraje',
            'transmision', 'combustible', 'precio',
            'descripcion', 'imagen'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }