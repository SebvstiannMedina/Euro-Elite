from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

from Main import views as main_views
from payments import views as pay_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Sitio
    path('', main_views.home, name='home'),
    path('contacto', main_views.contacto, name='contacto'),
    path('equipo', main_views.equipo, name='equipo'),
    path('productos', main_views.productos, name='productos'),
    path('perfil', main_views.perfil, name='perfil'),
    path('registro', main_views.registro, name='registro'),
    path('login', main_views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('agendar', main_views.agendar_cita, name='agendar'),
    path('mis_citas', main_views.mis_citas, name='mis_citas'),
    path('nueva_contrasena', main_views.nueva_contrasena, name='nueva_contrasena'),
    path('mis_pedidos', main_views.mis_pedidos, name='mis_pedidos'),
    path('resumen_compra', main_views.resumen_compra, name='resumen_compra'),
    path('confirmacion_datos', main_views.confirmacion_datos, name='confirmacion_datos'),
    path('carrito_compras', main_views.carrito_compras, name='carrito_compras'),
    path('terminos', main_views.terminos, name='terminos'),
    path('privacidad', main_views.privacidad, name='privacidad'),
    path('agregar_editar', main_views.agregar_editar, name='agregar_editar'),
    path('agregar_editar/<int:pk>/editar/', main_views.agregar_editar, name='editar_producto'),
    path('prueba', main_views.prueba, name='prueba'),
    path('compra_exitosa', main_views.compra_exitosa, name='compra_exitosa'),
    path('ofertas', main_views.ofertas, name='ofertas'),
    path('retiro_despacho', main_views.retiro_despacho, name='retiro_despacho'),
    path('admin_agendamientos', main_views.admin_agendamientos, name='admin_agendamiento'),
    path('admin_configuracion', main_views.admin_configuracion, name='admin_configuracion'),
    path('admin_dashboard', main_views.admin_dashboard, name='admin_dashboard'),
    path('admin_pedidos', main_views.admin_pedidos, name='admin_pedidos'),
    path('admin_reportes', main_views.admin_reportes, name='admin_reportes'),
    path('admin_usuarios', main_views.admin_usuarios, name='admin_usuarios'),
    path('estadistica', main_views.estadistica, name='estadistica'),
    path('producto/<int:pk>/', main_views.producto_detalle, name='producto_detalle'),
    # Carrito (server-first)
    path('carrito/agregar', main_views.cart_add, name='cart_add'),
    path('carrito/actualizar', main_views.cart_update, name='cart_update'),
    path('carrito/eliminar', main_views.cart_remove, name='cart_remove'),
    path('carrito/json', main_views.cart_json, name='cart_json'),
    # Checkout → redirige a Flow
    path('checkout/pagar', main_views.checkout_crear_pedido_y_pagar, name='checkout_pagar'),
    # Flow (payments)
    path("pagos/flow/crear/", pay_views.flow_crear_orden, name="flow_crear_orden"),
    path("pagos/flow/confirmacion/", pay_views.flow_confirmacion, name="flow_confirmacion"),
    path("pagos/flow/retorno/", pay_views.flow_retorno, name="flow_retorno"),
    path('custom_404', main_views.custom_404, name='custom_404'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'Main.views.custom_404'
