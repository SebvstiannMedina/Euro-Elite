from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.utils import timezone

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
class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        EMPLEADO = "EMPLEADO", "Empleado"
        CLIENTE = "CLIENTE", "Cliente"

    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    rol = models.CharField(max_length=12, choices=Rol.choices, default=Rol.CLIENTE, db_index=True)
    bloqueado = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.get_full_name() or self.username


class Direccion(MarcaTiempo):
    class Tipo(models.TextChoices):
        ENVIO = "ENVIO", "Envío"
        FACTURACION = "FACTURACION", "Facturación"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="direcciones")
    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.ENVIO)
    nombre_completo = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20, blank=True)
    linea1 = models.CharField(max_length=200)
    linea2 = models.CharField(max_length=200, blank=True)
    comuna = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100, default="Santiago")
    region = models.CharField(max_length=100, blank=True)
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

    categoria = models.ForeignKey(Categoria, null=True, blank=True, on_delete=models.SET_NULL, related_name="productos")

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

    @property
    def bajo_stock(self):
        return self.stock <= self.stock_minimo


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

    productos = models.ManyToManyField(Producto, related_name="promociones", blank=True)

    def __str__(self):
        return self.nombre

    def vigente(self):
        ahora = timezone.now()
        return self.activa and (not self.inicio or ahora >= self.inicio) and (not self.fin or ahora <= self.fin)


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
class Pedido(MarcaTiempo):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PAGADO = "PAGADO", "Pagado"
        PREPARACION = "PREPARACION", "En preparación"
        ENVIADO = "ENVIADO", "Enviado"
        ENTREGADO = "ENTREGADO", "Entregado"
        CANCELADO = "CANCELADO", "Cancelado"

    class MetodoEntrega(models.TextChoices):
        RETIRO = "RETIRO", "Retiro en tienda"
        DESPACHO = "DESPACHO", "Despacho a domicilio"

    class MetodoPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
        PASARELA = "PASARELA", "Pasarela"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pedidos")
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PENDIENTE, db_index=True)
    metodo_entrega = models.CharField(max_length=10, choices=MetodoEntrega.choices)
    metodo_pago = models.CharField(max_length=30, choices=MetodoPago.choices)

    direccion_envio = models.ForeignKey(Direccion, null=True, blank=True, on_delete=models.SET_NULL, related_name="envios")
    direccion_facturacion = models.ForeignKey(Direccion, null=True, blank=True, on_delete=models.SET_NULL, related_name="facturaciones")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    envio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def recalcular_totales(self):
        s = sum(i.subtotal for i in self.items.all())
        self.subtotal = s
        self.total = s - self.descuento + self.envio
        if self.total < 0:
            self.total = 0


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


class BloqueHorario(MarcaTiempo):
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name="bloques")
    inicio = models.DateTimeField(db_index=True)
    fin = models.DateTimeField(db_index=True)
    bloqueado = models.BooleanField(default=False)


class Cita(MarcaTiempo):
    class Estado(models.TextChoices):
        RESERVADA = "RESERVADA", "Reservada"
        COMPLETADA = "COMPLETADA", "Completada"
        CANCELADA = "CANCELADA", "Cancelada"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="citas")
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name="citas")
    bloque = models.OneToOneField(BloqueHorario, on_delete=models.PROTECT, related_name="cita")
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.RESERVADA)
    a_domicilio = models.BooleanField(default=False)
    direccion_domicilio = models.ForeignKey(Direccion, null=True, blank=True, on_delete=models.SET_NULL)


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
