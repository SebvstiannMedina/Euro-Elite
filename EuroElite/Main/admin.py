from django.contrib import admin
from .models import (
    Usuario, Direccion, Categoria, Producto, ImagenProducto,
    Promocion, CodigoDescuento, Carrito, ItemCarrito, Pedido, ItemPedido,
    Pago, Boleta, Resena, Servicio, Profesional,
    BloqueHorario, Cita, Banner, ConfigSitio, VehiculoEnVenta,
    VehiculoCliente, HistorialServicio, FotoNosotros, Contacto,
    RecordatorioMantenimiento, HorarioDia, HoraDisponible
)

# Usuarios personalizados
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'rol', 'is_active', 'bloqueado')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('rol', 'is_active', 'bloqueado')


@admin.register(CodigoDescuento)
class CodigoDescuentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'tipo', 'valor', 'activo', 'usos_actuales', 'usos_maximos', 'usos_por_usuario', 'inicio', 'fin')
    search_fields = ('codigo',)
    list_filter = ('activo', 'tipo')


@admin.register(VehiculoCliente)
class VehiculoClienteAdmin(admin.ModelAdmin):
    list_display = ('patente', 'marca', 'modelo', 'año', 'usuario', 'kilometraje_actual')
    search_fields = ('patente', 'marca', 'modelo', 'usuario__email')
    list_filter = ('marca', 'año')


@admin.register(HistorialServicio)
class HistorialServicioAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'fecha_ingreso', 'fecha_salida', 'estado', 'mecanico_asignado', 'costo_total')
    search_fields = ('vehiculo__patente', 'mecanico_asignado__email')
    list_filter = ('estado', 'fecha_ingreso')


@admin.register(FotoNosotros)
class FotoNosotrosAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'orden', 'activa', 'creado')
    search_fields = ('titulo',)
    list_filter = ('activa',)
    ordering = ('orden',)


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'asunto', 'leido', 'respondido', 'creado')
    search_fields = ('nombre', 'email', 'asunto')
    list_filter = ('leido', 'respondido', 'creado')
    ordering = ('-creado',)


@admin.register(RecordatorioMantenimiento)
class RecordatorioMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'vehiculo', 'tipo', 'fecha_programada', 'enviado', 'fecha_envio')
    search_fields = ('usuario__email', 'vehiculo__patente')
    list_filter = ('tipo', 'enviado', 'fecha_programada')


@admin.register(VehiculoEnVenta)
class VehiculoEnVentaAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'año', 'precio', 'usuario', 'estado', 'comision')
    search_fields = ('marca', 'modelo', 'usuario__email')
    list_filter = ('estado', 'marca', 'año')


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'calificacion', 'aprobada', 'creado')
    search_fields = ('usuario__email', 'producto__nombre')
    list_filter = ('aprobada', 'calificacion', 'creado')
    actions = ['aprobar_resenas', 'rechazar_resenas']

    def aprobar_resenas(self, request, queryset):
        queryset.update(aprobada=True)
    aprobar_resenas.short_description = "Aprobar reseñas seleccionadas"

    def rechazar_resenas(self, request, queryset):
        queryset.update(aprobada=False)
    rechazar_resenas.short_description = "Rechazar reseñas seleccionadas"

@admin.register(HorarioDia)
class HorarioDiaAdmin(admin.ModelAdmin):
    list_display = ("dia_semana", "hora_inicio", "hora_fin", "activo")
    list_filter = ("dia_semana", "activo")
    ordering = ("dia_semana", "hora_inicio")


@admin.register(HoraDisponible)
class HoraDisponibleAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora", "disponible", "creado")
    list_filter = ("disponible", "fecha", "hora")
    search_fields = ("fecha",)
    ordering = ("-fecha", "hora")
    date_hierarchy = "fecha"
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("horario_dia", "fecha", "hora", "creado", "actualizado")
        return ("creado", "actualizado")


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
admin.site.register(Servicio)
admin.site.register(Profesional)
admin.site.register(BloqueHorario)
admin.site.register(Cita)
admin.site.register(Banner)
admin.site.register(ConfigSitio)


