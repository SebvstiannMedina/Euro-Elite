from django.contrib import admin
from .models import (
    Usuario, Direccion, Categoria, Producto, ImagenProducto,
    Promocion, Carrito, ItemCarrito, Pedido, ItemPedido,
    Pago, Boleta, Resena, Servicio, Profesional,
    BloqueHorario, Cita, Banner, ConfigSitio
)

# Usuarios personalizados
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'is_active', 'bloqueado')
    search_fields = ('username', 'email')
    list_filter = ('rol', 'is_active', 'bloqueado')

# Otros modelos (registrados de manera básica)
admin.site.register(Direccion)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(ImagenProducto)
admin.site.register(Promocion)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(Pago)
admin.site.register(Boleta)
admin.site.register(Resena)
admin.site.register(Servicio)
admin.site.register(Profesional)
admin.site.register(BloqueHorario)
admin.site.register(Cita)
admin.site.register(Banner)
admin.site.register(ConfigSitio)

