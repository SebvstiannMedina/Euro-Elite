from django import forms
import unicodedata
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
        
        email = ''.join(email.split())
        
        dangerous_chars = ['<', '>', '"', "'", ';', '\\', '\r', '\n', '\t']
        for char in dangerous_chars:
            email = email.replace(char, '')
        
        email = email.lower()
        
        if len(email) < 5:
            raise forms.ValidationError('El correo electrónico debe tener al menos 5 caracteres.')
        if len(email) > 120:
            raise forms.ValidationError('El correo electrónico no puede tener más de 120 caracteres.')
        
        import re
        if not re.match(r'^[a-z0-9._+%-]+@[a-z0-9.-]+\.[a-z]{2,}$', email):
            raise forms.ValidationError('Formato de correo electrónico inválido.')
        
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
                'maxlength': '120',
                'oninput': "this.value=this.value.replace(/[\\s<>\"';]/g,'').toLowerCase().slice(0,120)"
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'oninput': "this.value=this.value.replace(/[^0-9]/g,'');",
                'maxlength': '8'
            }),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
        }

# ================= REGISTRO =================

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
from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Cita, Servicio, BloqueHorario, Direccion

class CitaForm(forms.ModelForm):
    """Formulario de agendamiento sin depender de profesionales."""

    class Meta:
        model = Cita
        fields = ["servicio", "bloque", "a_domicilio", "direccion_domicilio"]
        widgets = {
            "servicio": forms.Select(attrs={"class": "form-control"}),
            "bloque": forms.Select(attrs={"class": "form-control"}),
            "a_domicilio": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "direccion_domicilio": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # ✅ Crear servicios base si no existen
        servicios_base = [
            ("Diagnóstico general", 25000),
            ("Mantención básica", 35000),
            ("Cambio de aceite", 20000),
        ]
        for nombre, precio in servicios_base:
            Servicio.objects.get_or_create(nombre=nombre, defaults={"precio_base": precio, "activo": True})

        # ✅ Generar bloques si no hay
        self._generar_bloques_automaticos()

        # Mostrar solo servicios activos
        self.fields["servicio"].queryset = Servicio.objects.filter(activo=True)

        # ✅ Bloques disponibles (en hora local)
        ahora_local = timezone.localtime(timezone.now())
        self.fields["bloque"].queryset = BloqueHorario.objects.filter(
            bloqueado=False,
            cita__isnull=True,
            inicio__gte=ahora_local
        ).order_by("inicio")

        # ✅ Si el usuario tiene direcciones
        if user and user.is_authenticated:
            self.fields["direccion_domicilio"].queryset = Direccion.objects.filter(usuario=user)
        else:
            self.fields["direccion_domicilio"].queryset = Direccion.objects.none()

    def _generar_bloques_automaticos(self):
        """Crea horarios automáticos (09:00 a 17:00) en zona local."""
        hoy = timezone.localdate()
        if not BloqueHorario.objects.exists():
            tz = timezone.get_current_timezone()
            for dia in [hoy, hoy + timedelta(days=1)]:
                for hora in range(9, 18):  # 9 a 17
                    inicio_naive = datetime.combine(dia, datetime.min.time()) + timedelta(hours=hora)
                    inicio = timezone.make_aware(inicio_naive, tz)  # 👈 usa zona horaria local
                    fin = inicio + timedelta(hours=1)
                    BloqueHorario.objects.get_or_create(inicio=inicio, fin=fin, bloqueado=False)

    def clean(self):
        cleaned_data = super().clean()
        bloque = cleaned_data.get("bloque")

        if bloque and bloque.inicio <= timezone.now():
            raise forms.ValidationError("No puedes agendar en un bloque de tiempo pasado.")

        if bloque and hasattr(bloque, "cita"):
            raise forms.ValidationError("Este bloque ya está reservado.")

        # Validar domicilio
        if cleaned_data.get("a_domicilio") and not cleaned_data.get("direccion_domicilio"):
            self.add_error("direccion_domicilio", "Debes ingresar una dirección para el servicio a domicilio.")

        return cleaned_data


# ================= PRODUCTO =================
class ProductoForm(forms.ModelForm):
    promocion = forms.ModelChoiceField(
        queryset=Promocion.objects.filter(activa=True),
        required=False,
        label="Promoción",
        help_text="Selecciona una promoción o deja vacío si no aplica.",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Producto
        fields = [
            'nombre', 'sku', 'marca', 'descripcion',
            'precio', 'costo', 'stock', 'stock_minimo',
            'activo', 'categoria', 'imagen'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar opción vacía al select de promoción
        self.fields['promocion'].empty_label = "Sin promoción"
        
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
    """Formulario para editar o agregar dirección del usuario (sin código postal)."""
    
    comuna = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )
    
    class Meta:
        model = Direccion
        fields = ['linea1', 'linea2', 'comuna', 'region']

    @staticmethod
    def _normalize_text(value: str) -> str:
        s = (value or '').strip()
        s = unicodedata.normalize('NFD', s)
        s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
        return ''.join(ch for ch in s if ch.isalnum()).lower()

    @classmethod
    def _region_aliases(cls):
        return {
            "Aysén del Gral. Carlos Ibáñez del Campo": "Aysén",
            "Aysen del Gral. Carlos Ibanez del Campo": "Aysén",
            "Magallanes y de la Antártica Chilena": "Magallanes y la Antártica Chilena",
            "Magallanes y de la Antartica Chilena": "Magallanes y la Antártica Chilena",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Asegurar estilo bootstrap consistente para región
        self.fields['region'].widget.attrs.setdefault('class', 'form-select')
        self.fields['comuna'].widget.attrs.setdefault('class', 'form-select')

        saved_region = None
        if self.instance and getattr(self.instance, 'region', None):
            saved_region = self.instance.region
        elif 'initial' in kwargs and kwargs['initial'].get('region'):
            saved_region = kwargs['initial']['region']

        if saved_region:
            allowed_values = [val for (val, _label) in self.fields['region'].choices]
            aliases = self._region_aliases()
            canonical = aliases.get(saved_region, saved_region)

            if canonical in allowed_values:
                self.initial['region'] = canonical
            elif saved_region not in allowed_values:
                self.fields['region'].choices = [(saved_region, saved_region)] + list(self.fields['region'].choices)
                self.initial['region'] = saved_region

        # Inyectar la comuna guardada como opción temporal para que el select muestre el valor correcto
        saved_comuna = None
        if self.instance and getattr(self.instance, 'comuna', None):
            saved_comuna = self.instance.comuna
        elif 'initial' in kwargs and kwargs['initial'].get('comuna'):
            saved_comuna = kwargs['initial']['comuna']

        if saved_comuna:
            # Establecer una opción inicial con la comuna guardada
            current_choices = list(getattr(self.fields['comuna'].widget, 'choices', []))
            if not any(val == saved_comuna for val, _ in current_choices):
                self.fields['comuna'].widget.choices = [(saved_comuna, saved_comuna)] + current_choices
            self.initial['comuna'] = saved_comuna

    def clean_region(self):
        region = (self.cleaned_data.get('region') or '').strip()
        if not region:
            return region

        allowed_values = [val for (val, _label) in self.fields['region'].choices]
        if region in allowed_values:
            return region

        # Intentar mapear alias conocidos
        aliases = self._region_aliases()
        if region in aliases:
            return aliases[region]

        # Fallback: comparar de forma insensible a tildes y mayúsculas
        norm = self._normalize_text
        for val in allowed_values:
            if norm(val) == norm(region):
                return val

        # Si no encontramos mapeo, devolvemos lo recibido (se guardará tal cual)
        return region
    
    def clean_linea1(self):
        linea1 = (self.cleaned_data.get('linea1') or '').strip()
        if len(linea1) < 3:
            raise forms.ValidationError('La dirección debe tener al menos 3 caracteres.')
        if len(linea1) > 65:
            raise forms.ValidationError('La dirección no puede tener más de 65 caracteres.')
        return linea1
    
    def clean_linea2(self):
        linea2 = (self.cleaned_data.get('linea2') or '').strip()
        if linea2 and len(linea2) < 3:
            raise forms.ValidationError('El departamento/oficina debe tener al menos 3 caracteres.')
        if len(linea2) > 65:
            raise forms.ValidationError('El departamento/oficina no puede tener más de 65 caracteres.')
        return linea2
    
        widgets = {
            'linea1': forms.TextInput(attrs={
                'class': 'form-control',
                'oninput': "this.value=this.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9# ]/g,'');",
                'minlength': '3',
                'maxlength': '65'
            }),
            'linea2': forms.TextInput(attrs={
                'class': 'form-control',
                'oninput': "this.value=this.value.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 ]/g,'');",
                'minlength': '3',
                'maxlength': '65'
            }),
            'region': forms.Select(attrs={'class': 'form-select', 'required': True}),
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

from django.contrib.auth.forms import AuthenticationForm

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            "autofocus": True,
            "class": "form-control",
            "placeholder": "Ingresa tu correo"
        })
    )

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