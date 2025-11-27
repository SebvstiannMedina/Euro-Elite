from django import forms
import unicodedata
import re
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Q

from .models import Cita, BloqueHorario, Servicio, Producto, Direccion, Promocion, HorarioDia

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

class CitaForm(forms.ModelForm):

    fecha = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=True
    )

    class Meta:
        model = Cita
        fields = ["servicio", "fecha", "bloque", "a_domicilio", "direccion_domicilio"]
        widgets = {
            "servicio": forms.Select(attrs={"class": "form-control"}),
            "bloque": forms.Select(attrs={"class": "form-control"}),
            "a_domicilio": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "direccion_domicilio": forms.TextInput(attrs={"class": "form-control", "maxlength": "150"}),
        }

    def __init__(self, *args, **kwargs):
        from .models import HoraDisponible
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # --- Servicios Base ---
        servicios_base = [
            ("Diagnóstico general", 25000),
            ("Mantención básica", 35000),
            ("Cambio de aceite", 20000),
        ]
        for nombre, precio in servicios_base:
            Servicio.objects.get_or_create(
                nombre=nombre,
                defaults={"precio_base": precio, "activo": True}
            )
        self.fields["servicio"].queryset = Servicio.objects.filter(activo=True)

        # --- Bloques vacíos por defecto ---
        self.fields["bloque"].queryset = BloqueHorario.objects.none()

        # --- Cuando el usuario selecciona una fecha ---
        if "fecha" in self.data:
            try:
                fecha_str = self.data.get("fecha")
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

                # Crear bloques dinámicamente desde HoraDisponible registradas
                self._generar_bloques_desde_disponibles(fecha)

                # Cargar solo bloques que tengan HoraDisponible asociada
                horas_disponibles = HoraDisponible.objects.filter(
                    fecha=fecha,
                    disponible=True
                ).values_list('hora', flat=True).distinct()

                # Filtrar bloques que coincidan con horas disponibles
                bloques_disponibles = []
                for hora_disp in horas_disponibles:
                    # Encontrar bloques que comiencen con esa hora
                    from datetime import datetime as dt
                    tz = timezone.get_current_timezone()
                    inicio_aware = timezone.make_aware(dt.combine(fecha, hora_disp), tz)
                    
                    # Buscar bloque que tenga esa hora inicio
                    bloque = BloqueHorario.objects.filter(
                        inicio__date=fecha,
                        inicio__hour=hora_disp.hour
                    ).first()
                    
                    if bloque and not Cita.objects.filter(bloque=bloque, estado="RESERVADA").exists():
                        bloques_disponibles.append(bloque.id)
                
                self.fields["bloque"].queryset = BloqueHorario.objects.filter(
                    id__in=bloques_disponibles
                ).order_by("inicio")
                
            except Exception as e:
                print(f"Error cargando bloques: {e}")
                pass

        # --- En caso de edición ---
        elif self.instance.pk and self.instance.bloque:
            fecha = self.instance.bloque.inicio.date()
            self.fields["fecha"].initial = fecha
            self.fields["bloque"].queryset = (
                BloqueHorario.objects.filter(inicio__date=fecha)
            )

    # ===================== MÉTODO INTERNO =====================
    def _generar_bloques_desde_disponibles(self, fecha):
        """Crea bloques a partir de horas disponibles registradas."""
        from .models import HoraDisponible
        from datetime import datetime as dt
        
        # Obtener horas disponibles para esa fecha
        horas_disponibles = HoraDisponible.objects.filter(
            fecha=fecha,
            disponible=True
        ).values_list('hora', flat=True).distinct()

        tz = timezone.get_current_timezone()

        for hora in horas_disponibles:
            inicio_naive = dt.combine(fecha, hora)
            inicio = timezone.make_aware(inicio_naive, tz)
            fin = inicio + timedelta(hours=1)

            BloqueHorario.objects.get_or_create(
                inicio=inicio,
                fin=fin,
                bloqueado=False
            )

    # ===================== VALIDACIONES =====================
    def clean_bloque(self):
        """Permite cualquier BloqueHorario válido, no solo los del queryset inicial."""
        bloque_id = self.data.get("bloque")
        if not bloque_id:
            return None
        
        try:
            bloque = BloqueHorario.objects.get(id=bloque_id)
            return bloque
        except BloqueHorario.DoesNotExist:
            raise forms.ValidationError("Horario inválido.")
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha")
        bloque = cleaned_data.get("bloque")

        if fecha and fecha < timezone.localdate():
            raise forms.ValidationError("No puedes seleccionar una fecha pasada.")

        if bloque and bloque.inicio <= timezone.now():
            raise forms.ValidationError("El horario ya pasó.")

        if bloque and Cita.objects.filter(bloque=bloque, estado="RESERVADA").exists():
            raise forms.ValidationError("Este bloque ya está reservado.")

        if cleaned_data.get("a_domicilio") and not cleaned_data.get("direccion_domicilio"):
            self.add_error("direccion_domicilio", "Debes ingresar la dirección.")

        return cleaned_data

    # ===================== SAVE =====================
    def save(self, commit=True):
        from .models import HoraDisponible
        cita = super().save(commit=False)
        
        # Marcar la hora disponible como ocupada
        if cita.bloque:
            fecha = cita.bloque.inicio.date()
            hora = cita.bloque.inicio.time()
            
            hora_disp = HoraDisponible.objects.filter(
                fecha=fecha,
                hora=hora
            ).first()
            
            if hora_disp:
                hora_disp.disponible = False
                hora_disp.save(update_fields=['disponible'])
        
        if commit:
            cita.save()
        return cita

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
    imagenes = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control', 'multiple': ''}),
        label='Imágenes del vehículo (puedes seleccionar varias)',
        help_text='Selecciona hasta 10 imágenes de tu vehículo. La primera será la imagen principal.'
    )

    class Meta:
        model = VehiculoEnVenta
        fields = [
            'marca', 'modelo', 'año', 'patente', 'kilometraje',
            'transmision', 'combustible', 'color', 'precio',
            'descripcion'
        ]
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Toyota, Ford, Chevrolet'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corolla, Focus, Cruze'}),
            'año': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2020', 'min': '1900', 'max': '2025'}),
            'patente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ABCD12', 'style': 'text-transform: uppercase'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50000', 'min': '0'}),
            'transmision': forms.Select(attrs={'class': 'form-select'}),
            'combustible': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Blanco, Negro, Gris'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10000000', 'min': '0', 'step': '100000'}),
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Describe las características y estado de tu vehículo...'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'año': 'Año',
            'patente': 'Patente',
            'kilometraje': 'Kilometraje (km)',
            'precio': 'Precio (CLP)',
            'descripcion': 'Descripción',
        }

    # -----------------
    # Validaciones
    # -----------------
    def clean_marca(self):
        marca = (self.cleaned_data.get('marca') or '').strip()
        if not marca:
            raise forms.ValidationError('La marca es obligatoria.')
        # Solo letras, números y espacios
        if not re.match(r'^[a-zA-Z0-9\s\-áéíóúÁÉÍÓÚ]+$', marca):
            raise forms.ValidationError('La marca solo puede contener letras, números y guiones.')
        if len(marca) > 50:
            raise forms.ValidationError('La marca no puede exceder 50 caracteres.')
        return marca.title()

    def clean_modelo(self):
        modelo = (self.cleaned_data.get('modelo') or '').strip()
        if not modelo:
            raise forms.ValidationError('El modelo es obligatorio.')
        # Solo letras, números y espacios
        if not re.match(r'^[a-zA-Z0-9\s\-áéíóúÁÉÍÓÚ]+$', modelo):
            raise forms.ValidationError('El modelo solo puede contener letras, números y guiones.')
        if len(modelo) > 50:
            raise forms.ValidationError('El modelo no puede exceder 50 caracteres.')
        return modelo.title()

    def clean_año(self):
        anio = self.cleaned_data.get('año')
        if anio is None:
            raise forms.ValidationError('El año es obligatorio.')
        current_year = datetime.now().year
        if anio < 1950 or anio > current_year + 1:
            raise forms.ValidationError(f"El año debe estar entre 1950 y {current_year + 1}.")
        return anio

    def clean_kilometraje(self):
        km = self.cleaned_data.get('kilometraje')
        if km is None:
            raise forms.ValidationError('El kilometraje es obligatorio.')
        if km < 0:
            raise forms.ValidationError('El kilometraje no puede ser negativo.')
        if km > 999999:
            raise forms.ValidationError('El kilometraje no puede exceder 999999 km.')
        return km

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is None:
            raise forms.ValidationError('El precio es obligatorio.')
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        if precio > 9999999999:
            raise forms.ValidationError('El precio es demasiado alto.')
        return precio

    def clean_patente(self):
        patente = (self.cleaned_data.get('patente') or '').upper().strip()
        if patente:
            # Solo letras y números, máximo 6 caracteres
            patente = patente.replace(' ', '').replace('-', '')
            if not re.match(r'^[A-Z0-9]{1,6}$', patente):
                raise forms.ValidationError('La patente debe tener máximo 6 caracteres alfanuméricos.')
            if len(patente) > 6:
                raise forms.ValidationError('La patente no puede exceder 6 caracteres.')
        return patente

    def clean_color(self):
        color = (self.cleaned_data.get('color') or '').strip()
        if color:
            # Solo letras y espacios
            if not re.match(r'^[a-zA-Z\s\-áéíóúÁÉÍÓÚ]+$', color):
                raise forms.ValidationError('El color solo puede contener letras.')
            if len(color) > 30:
                raise forms.ValidationError('El color no puede exceder 30 caracteres.')
            return color.title()
        return color

    def clean_descripcion(self):
        desc = (self.cleaned_data.get('descripcion') or '').strip()
        if desc:
            # Letras, números, espacios y símbolos simples: .,!?;:-()
            if not re.match(r'^[a-zA-Z0-9\s\.\,\!\?\;\:\-\(\)áéíóúÁÉÍÓÚ\n\r]+$', desc):
                raise forms.ValidationError('La descripción contiene caracteres no permitidos.')
            if len(desc) > 2000:
                raise forms.ValidationError('La descripción no puede exceder 2000 caracteres.')
        return desc

    def clean_imagenes(self):
        # Al ser un campo con multiple, Django no lo maneja automáticamente
        # usamos self.files.getlist para validar todas
        files = self.files.getlist('imagenes')
        if not files:
            return None
        if len(files) > 10:
            raise forms.ValidationError('Puedes subir como máximo 10 imágenes.')
        allowed = {'image/jpeg', 'image/png', 'image/webp'}
        max_mb = 5 * 1024 * 1024
        for f in files:
            if f.content_type not in allowed:
                raise forms.ValidationError('Solo se permiten imágenes JPG, PNG o WEBP.')
            if f.size > max_mb:
                raise forms.ValidationError('Cada imagen debe pesar como máximo 5 MB.')
        # Devolvemos la lista para poder usarla si el llamador la requiere
        return files

from django import forms
from .models import Pedido

class ConfirmarEntregaForm(forms.ModelForm):

    # Firmas viene desde un input hidden (base64)
    firma_entrega_hidden = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Pedido
        fields = [
            "receptor_nombre",
            "receptor_rut",
            "observacion_entrega",
            "foto_entrega",
            "firma_entrega_hidden",
        ]

        widgets = {
            "receptor_nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre de quien recibe",
                "required": True,
            }),
            "receptor_rut": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "12345678-9 / DNI",
            }),
            "observacion_entrega": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Observación opcional",
            }),
            "foto_entrega": forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
                "capture": "camera",  # abre cámara en teléfono
            }),
        }

class HorarioDiaForm(forms.ModelForm):
    class Meta:
        model = HorarioDia
        fields = ["dia_semana", "hora_inicio", "hora_fin", "activo"]
        widgets = {
            "dia_semana": forms.Select(attrs={"class": "form-select"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "hora_fin": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
