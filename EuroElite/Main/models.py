from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from django.utils import timezone
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

# =============================
#   BASE: timestamps genéricos
# =============================
class MarcaTiempo(models.Model):
    creado = models.DateTimeField(auto_now_add=True, db_index=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# =============================
#   USUARIOS Y DIRECCIONES
# =============================
from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


# --- MANAGER PERSONALIZADO ---
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("rol", "ADMIN")  # 👈 opcional: superusers como admin

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# --- MODELO USUARIO ---
class Usuario(AbstractUser):
    username = None  
    email = models.EmailField(unique=True)

    telefono = models.CharField(max_length=20, blank=True, null=True)
    rut = models.CharField(max_length=12, blank=True, null=True, unique=True)

    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        CLIENTE = "CLIENTE", "Cliente"
        MECANICO = "MECANICO", "Mecánico"
        RETIRO = "RETIRO", "Encargado de Retiro"
        DESPACHO = "DESPACHO", "Encargado de Despacho"
        REPARTIDOR = "REPARTIDOR", "Repartidor"
        ASIGNADOR = "ASIGNADOR", "Asignador de pedidos"

    rol = models.CharField(max_length=12, choices=Rol.choices, default=Rol.CLIENTE, db_index=True)
    bloqueado = models.BooleanField(default=False)
    accept_legal_terms = models.BooleanField(default=False)

    USERNAME_FIELD = "email"                       # login con email
    REQUIRED_FIELDS = ["first_name", "last_name"]  # se piden en createsuperuser

    objects = UsuarioManager()  # 👈 aquí va tu manager personalizado

    def __str__(self):
        return self.get_full_name() or self.email

class Direccion(MarcaTiempo):
    class Tipo(models.TextChoices):
        ENVIO = "ENVIO", "Envío"
        FACTURACION = "FACTURACION", "Facturación"

    REGIONES_CHILE = [
        ("Arica y Parinacota", "Arica y Parinacota"),
        ("Tarapacá", "Tarapacá"),
        ("Antofagasta", "Antofagasta"),
        ("Atacama", "Atacama"),
        ("Coquimbo", "Coquimbo"),
        ("Valparaíso", "Valparaíso"),
        ("Metropolitana de Santiago", "Metropolitana de Santiago"),
        ("O'Higgins", "O'Higgins"),
        ("Maule", "Maule"),
        ("Ñuble", "Ñuble"),
        ("Biobío", "Biobío"),
        ("La Araucanía", "La Araucanía"),
        ("Los Ríos", "Los Ríos"),
        ("Los Lagos", "Los Lagos"),
        ("Aysén", "Aysén"),
        ("Magallanes y la Antártica Chilena", "Magallanes y la Antártica Chilena"),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="direcciones")
    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.ENVIO)
    nombre_completo = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20, blank=True)
    linea1 = models.CharField(max_length=200)
    linea2 = models.CharField(max_length=200, blank=True)
    comuna = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100, default="Santiago")
    region = models.CharField(max_length=50, choices=REGIONES_CHILE, blank=True)
    codigo_postal = models.CharField(max_length=20, blank=True)
    predeterminada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre_completo} - {self.linea1}"


# =============================
#   CATÁLOGO Y PRODUCTOS
# =============================
class Categoria(MarcaTiempo):
    nombre = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    padre = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="hijos")
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Producto(MarcaTiempo):
    nombre = models.CharField(max_length=200, db_index=True)
    sku = models.CharField(max_length=60, unique=True)
    marca = models.CharField(max_length=80, blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    costo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=3)
    activo = models.BooleanField(default=True)
    categoria = models.ForeignKey(
        Categoria, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="productos"
    )
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

    @property
    def bajo_stock(self):
        return self.stock <= self.stock_minimo


    @property
    def promocion_vigente(self):
        ahora = timezone.now()
        return (
            self.promociones.filter(
                activa=True
            )
            .filter(models.Q(inicio__isnull=True) | models.Q(inicio__lte=ahora))
            .filter(models.Q(fin__isnull=True) | models.Q(fin__gte=ahora))
            .order_by('-valor')
            .first()
        )


    @property
    def precio_con_descuento(self):
        promo = self.promocion_vigente
        if promo:
            if promo.tipo == Promocion.Tipo.PORCENTAJE:
                descuento = (self.precio * promo.valor) / Decimal(100)
                return (self.precio - descuento).quantize(Decimal('0.01'))
            elif promo.tipo == Promocion.Tipo.MONTO:
                return max(self.precio - promo.valor, Decimal('0.00')).quantize(Decimal('0.01'))
        return self.precio


class ImagenProducto(MarcaTiempo):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to="productos/")
    texto_alt = models.CharField(max_length=150, blank=True)
    posicion = models.PositiveSmallIntegerField(default=0)


# =============================
#   PROMOCIONES Y OFERTAS
# =============================
class Promocion(MarcaTiempo):
    class Tipo(models.TextChoices):
        PORCENTAJE = "PORCENTAJE", "Porcentaje"
        MONTO = "MONTO", "Monto fijo"

    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.PORCENTAJE)
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    inicio = models.DateTimeField(null=True, blank=True)
    fin = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    mostrar_en_inicio = models.BooleanField(default=False)

    productos = models.ManyToManyField("Producto", related_name="promociones", blank=True)

    def __str__(self):
        if self.tipo == self.Tipo.PORCENTAJE:
            return f"{self.nombre} (-{self.valor}%)"
        else:
            return f"{self.nombre} (-${self.valor:,.0f})"

    def vigente(self):
        """Comprueba si la promoción está activa en la fecha actual."""
        ahora = timezone.now()
        return (
            self.activa and
            (not self.inicio or self.inicio <= ahora) and
            (not self.fin or self.fin >= ahora)
        )


# =============================
#   CÓDIGOS DE DESCUENTO
# =============================
class CodigoDescuento(MarcaTiempo):
    class Tipo(models.TextChoices):
        PORCENTAJE = "PORCENTAJE", "Porcentaje"
        MONTO = "MONTO", "Monto fijo"

    codigo = models.CharField(max_length=50, unique=True, db_index=True)
    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.PORCENTAJE)
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    inicio = models.DateTimeField(null=True, blank=True)
    fin = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    usos_maximos = models.PositiveIntegerField(null=True, blank=True, help_text="Cantidad máxima de veces que se puede usar este código")
    usos_actuales = models.PositiveIntegerField(default=0)
    usos_por_usuario = models.PositiveIntegerField(null=True, blank=True, help_text="Veces máximas que un mismo usuario puede usar este código")
    monto_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monto mínimo de compra para aplicar el descuento")

    def __str__(self):
        return f"{self.codigo} (-{self.valor}{'%' if self.tipo == self.Tipo.PORCENTAJE else ' CLP'})"

    def es_valido(self):
        """Verifica si el código es válido para usar."""
        ahora = timezone.now()
        if not self.activo:
            return False, "El código no está activo"
        if self.inicio and self.inicio > ahora:
            return False, "El código aún no está disponible"
        if self.fin and self.fin < ahora:
            return False, "El código ha expirado"
        if self.usos_maximos and self.usos_actuales >= self.usos_maximos:
            return False, "El código ha alcanzado el límite de usos"
        return True, "Código válido"

    def calcular_descuento(self, subtotal):
        """Calcula el descuento aplicable al subtotal."""
        if subtotal < self.monto_minimo:
            return Decimal('0.00')
        
        if self.tipo == self.Tipo.PORCENTAJE:
            descuento = (subtotal * self.valor) / Decimal(100)
        else:
            descuento = self.valor
        
        # No puede ser mayor al subtotal
        return min(descuento, subtotal).quantize(Decimal('0.01'))


# =============================
#   CARRITO DE COMPRAS
# =============================
class Carrito(MarcaTiempo):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="carritos")
    clave_sesion = models.CharField(max_length=80, blank=True, db_index=True)
    activo = models.BooleanField(default=True)

    def subtotal(self):
        return sum(i.subtotal for i in self.items.select_related("producto"))


class ItemCarrito(MarcaTiempo):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = [("carrito", "producto")]

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


# =============================
#   PEDIDOS, PAGOS Y BOLETAS
# =============================
from django.db import models
from django.conf import settings
from django.utils import timezone


from django.db import models
from django.conf import settings
from django.utils import timezone


from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PAGADO = "PAGADO", "Pagado"
        PREPARACION = "PREPARACION", "En preparación"
        EN_RUTA = "EN_RUTA", "En ruta"
        ENVIADO = "ENVIADO", "Enviado"
        ENTREGADO = "ENTREGADO", "Entregado"
        CANCELADO = "CANCELADO", "Cancelado"

    class MetodoEntrega(models.TextChoices):
        RETIRO = "RETIRO", "Retiro en tienda"
        DESPACHO = "DESPACHO", "Despacho a domicilio"

    class MetodoPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
        PASARELA = "PASARELA", "Pasarela de pago"

    # RELACIONES PRINCIPALES
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="Cliente"
    )

    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entregas_asignadas",
        verbose_name="Empleado asignado"
    )

    asignado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asignaciones_realizadas",
        verbose_name="Asignador"
    )

    # ESTADO / ENTREGA / PAGO
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE, db_index=True)
    metodo_entrega = models.CharField(max_length=10, choices=MetodoEntrega.choices)
    metodo_pago = models.CharField(max_length=30, choices=MetodoPago.choices)

    direccion_envio = models.ForeignKey("Direccion", null=True, blank=True, on_delete=models.SET_NULL, related_name="envios")
    direccion_facturacion = models.ForeignKey("Direccion", null=True, blank=True, on_delete=models.SET_NULL, related_name="facturaciones")

    # TOTALES
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    codigo_descuento = models.ForeignKey("CodigoDescuento", null=True, blank=True, on_delete=models.SET_NULL, related_name="pedidos")
    envio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # ENTREGA REGISTRO
    entregado_por = models.CharField(max_length=100, blank=True, null=True)
    hora_entrega = models.TimeField(blank=True, null=True)
    observacion_entrega = models.TextField(blank=True, null=True)

    receptor_nombre = models.CharField(max_length=200, blank=True, null=True)
    receptor_rut = models.CharField(max_length=30, blank=True, null=True)

    firma_entrega = models.ImageField(
        upload_to="firmas/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['png','jpg','jpeg'])]
    )

    foto_entrega = models.ImageField(
        upload_to="entregas/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['png','jpg','jpeg'])]
    )

    # TIEMPOS
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    # MÉTODOS ÚTILES
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.email} ({self.get_estado_display()})"

    def recalcular_totales(self):
        s = sum(i.subtotal for i in self.items.all())
        self.subtotal = s
        self.total = s - self.descuento + self.envio
        if self.total < 0:
            self.total = 0
        self.save()

    def marcar_en_ruta(self):
        self.estado = self.Estado.EN_RUTA
        self.save()

    def marcar_como_entregado(self, empleado_nombre):
        self.estado = self.Estado.ENTREGADO
        self.entregado_por = empleado_nombre
        self.hora_entrega = timezone.localtime().time()
        self.save()

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"




class ItemPedido(MarcaTiempo):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    nombre_producto = models.CharField(max_length=200)
    sku_producto = models.CharField(max_length=60)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


class Pago(MarcaTiempo):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        COMPLETADO = "COMPLETADO", "Completado"
        FALLIDO = "FALLIDO", "Fallido"

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="pago")
    metodo = models.CharField(max_length=30, choices=Pedido.MetodoPago.choices)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    
    # Campos para integración con Flow
    flow_token = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    commerce_order = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    flow_response = models.TextField(blank=True, null=True)  # Respuesta cruda de Flow para auditoría


class Boleta(MarcaTiempo):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="boleta")
    numero = models.CharField(max_length=40, unique=True)
    pdf = models.FileField(upload_to="boletas/", blank=True)
    enviada = models.DateTimeField(null=True, blank=True)


# =============================
#   RESEÑAS
# =============================
class Resena(MarcaTiempo):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="resenas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resenas")
    calificacion = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    privada_admin = models.BooleanField(default=False)
    aprobada = models.BooleanField(default=False)


# =============================
#   SERVICIOS Y AGENDAS
# =============================
class Servicio(MarcaTiempo):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    a_domicilio = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Profesional(MarcaTiempo):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil_profesional")
    especialidad = models.CharField(max_length=120, blank=True)
    activo = models.BooleanField(default=True)

from django.db import models
from django.utils.timezone import localtime

class BloqueHorario(models.Model):
    inicio = models.DateTimeField(db_index=True)
    fin = models.DateTimeField(db_index=True)
    bloqueado = models.BooleanField(default=False)

    def __str__(self):
        inicio_local = localtime(self.inicio)
        fin_local = localtime(self.fin)
        return f"{inicio_local.strftime('%d/%m/%Y %H:%M')} - {fin_local.strftime('%H:%M')}"


class Cita(MarcaTiempo):
    class Estado(models.TextChoices):
        RESERVADA = "RESERVADA", "Reservada"
        COMPLETADA = "COMPLETADA", "Completada"
        CANCELADA = "CANCELADA", "Cancelada"
        EN_PROCESO = "EN_PROCESO", "En proceso"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="citas")
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name="citas")

    bloque = models.ForeignKey(
        BloqueHorario,
        on_delete=models.PROTECT,
        related_name="citas"
    )

    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.RESERVADA)
    a_domicilio = models.BooleanField(default=False)
    direccion_domicilio = models.CharField(max_length=255, null=True, blank=True)


# =============================
#   CONFIGURACIÓN DEL SITIO
# =============================
class Banner(MarcaTiempo):
    titulo = models.CharField(max_length=120)
    imagen = models.ImageField(upload_to="banners/")
    url = models.URLField(blank=True)
    activo = models.BooleanField(default=True)


class ConfigSitio(MarcaTiempo):
    habilitar_efectivo = models.BooleanField(default=True)
    habilitar_transferencia = models.BooleanField(default=True)
    habilitar_pasarela = models.BooleanField(default=True)
    costo_envio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    envio_gratis_desde = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

from django.contrib.auth.models import BaseUserManager

from django.contrib.auth.models import User

from django.db import models
from django.conf import settings

class VehiculoEnVenta(models.Model):
    TRANSMISIONES = [
        ('manual', 'Manual'),
        ('automatica', 'Automática'),
    ]

    COMBUSTIBLES = [
        ('bencina', 'Bencina'),
        ('diesel', 'Diésel / Petrolero'),
    ]

    ESTADOS = [
        ('pendiente', 'Pendiente de aprobación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('vendido', 'Vendido'),
        ('oculto', 'Oculto'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehiculos_publicados'
    )
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.PositiveIntegerField()
    # Permitir guardar registros existentes sin valor inicial y completar luego
    patente = models.CharField(max_length=10, help_text="Patente del vehículo", blank=True, default="")
    kilometraje = models.PositiveIntegerField(help_text="Kilómetros recorridos")
    transmision = models.CharField(max_length=20, choices=TRANSMISIONES)
    combustible = models.CharField(max_length=20, choices=COMBUSTIBLES)
    # Color puede ser opcional al inicio
    color = models.CharField(max_length=30, help_text="Color del vehículo", blank=True, default="")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='vehiculos/', blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    comision = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Comisión por venta")

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.año}) - {self.usuario.email}"

    # Alias compatible para plantillas que usan "anio"
    @property
    def anio(self):
        return self.año


class VehiculoImagen(models.Model):
    vehiculo = models.ForeignKey(
        VehiculoEnVenta,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='vehiculos/')
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'fecha_subida']

    def __str__(self):
        return f"Imagen {self.orden} - {self.vehiculo.marca} {self.vehiculo.modelo}"


# =============================
#   VEHÍCULO Y HISTORIAL DE SERVICIOS
# =============================
class VehiculoCliente(MarcaTiempo):
    """Vehículo registrado por un cliente para seguimiento de servicios."""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehiculos")
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.PositiveIntegerField()
    color = models.CharField(max_length=30, blank=True)
    kilometraje_actual = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.patente}"


class HistorialServicio(MarcaTiempo):
    """Registro de servicios realizados a un vehículo."""
    vehiculo = models.ForeignKey(VehiculoCliente, on_delete=models.CASCADE, related_name="historial")
    cita = models.OneToOneField(Cita, on_delete=models.SET_NULL, null=True, blank=True, related_name="historial")
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    fecha_salida = models.DateTimeField(null=True, blank=True)
    mecanico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="servicios_realizados"
    )
    descripcion_trabajo = models.TextField()
    estado = models.CharField(
        max_length=20,
        choices=[
            ('en_espera', 'En espera'),
            ('en_proceso', 'En proceso'),
            ('completado', 'Completado'),
            ('entregado', 'Entregado'),
        ],
        default='en_espera'
    )
    comentario_mecanico = models.TextField(blank=True)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    kilometraje = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.vehiculo.patente} - {self.fecha_ingreso.strftime('%d/%m/%Y')}"


# =============================
#   GALERÍA PÁGINA NOSOTROS
# =============================
class FotoNosotros(MarcaTiempo):
    """Fotos editables para la página Nosotros."""
    titulo = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='nosotros/')
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['orden', '-creado']
        verbose_name = "Foto de Nosotros"
        verbose_name_plural = "Fotos de Nosotros"
    
    def __str__(self):
        return self.titulo


# =============================
#   CONTACTO
# =============================
class Contacto(MarcaTiempo):
    """Mensajes de contacto del formulario."""
    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    respondido = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-creado']
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
    
    def __str__(self):
        return f"{self.nombre} - {self.asunto}"


# =============================
#   RECORDATORIOS DE MANTENIMIENTO
# =============================
class RecordatorioMantenimiento(MarcaTiempo):
    """Recordatorios automáticos de mantenimiento para clientes."""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recordatorios")
    vehiculo = models.ForeignKey(VehiculoCliente, on_delete=models.CASCADE, related_name="recordatorios")
    tipo = models.CharField(
        max_length=50,
        choices=[
            ('tiempo', 'Por tiempo'),
            ('kilometraje', 'Por kilometraje'),
        ]
    )
    fecha_programada = models.DateField()
    kilometraje_programado = models.PositiveIntegerField(null=True, blank=True)
    mensaje = models.TextField()
    enviado = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Recordatorio para {self.usuario.email} - {self.fecha_programada}"

class HorarioDia(models.Model):
    DIA_CHOICES = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    dia_semana = models.IntegerField(choices=DIA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_dia_semana_display()}: {self.hora_inicio} - {self.hora_fin}"
