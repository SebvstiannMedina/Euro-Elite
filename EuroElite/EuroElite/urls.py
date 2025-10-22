from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from Main import views as main_views
from payments import views as pay_views
from Main.views import CustomLoginView, registro
from django.contrib import admin
from django.urls import path, include
from Main.views import CustomLoginView, CustomLogoutView, registro
from Main import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Sitio
    path('', main_views.home, name='home'),
    path('nosotros', main_views.nosotros, name='nosotros'),
    path('equipo', main_views.equipo, name='equipo'),
    path('productos', main_views.productos, name='productos'),
    path('perfil', main_views.perfil, name='perfil'),
    path('registro', main_views.registro, name='registro'),
    path('login', CustomLoginView.as_view(template_name='taller/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('agendar', main_views.agendar, name='agendar'),
    path('mis_citas', main_views.mis_citas, name='mis_citas'),
    path('citas/<int:cita_id>/anular/', main_views.anular_cita, name='anular_cita'),
    path('mis_pedidos', main_views.mis_pedidos, name='mis_pedidos'),
    path('resumen_compra', main_views.resumen_compra, name='resumen_compra'),
    path('confirmacion_datos', main_views.confirmacion_datos, name='confirmacion_datos'),
    path('carrito_compras', main_views.carrito_compras, name='carrito_compras'),
    path('carrito/json/', main_views.carrito_json, name='carrito_json'),
    path('terminos', main_views.terminos, name='terminos'),
    path('privacidad', main_views.privacidad, name='privacidad'),
    path('agregar_editar', main_views.agregar_editar, name='agregar_editar'),
    path('agregar_editar/<int:pk>/editar/', main_views.agregar_editar, name='editar_producto'),
    path('prueba', main_views.prueba, name='prueba'),
    path('compra_exitosa/', main_views.compra_exitosa, name='compra_exitosa'),
    path('compra_exitosa/<int:pedido_id>/', main_views.compra_exitosa, name='compra_exitosa_detalle'),
    path('ofertas', main_views.ofertas, name='ofertas'),
    path('retiro_despacho', main_views.retiro_despacho, name='retiro_despacho'),
    path('admin_agendamientos', main_views.admin_agendamientos, name='admin_agendamiento'),
    path('admin_configuracion', main_views.admin_configuracion, name='admin_configuracion'),
    path('admin_dashboard', main_views.admin_dashboard, name='admin_dashboard'),
    path('admin_pedidos', main_views.admin_pedidos, name='admin_pedidos'),
    path('admin_reportes', main_views.admin_reportes, name='admin_reportes'),
    path('admin_usuarios', main_views.admin_usuarios, name='admin_usuarios'),
    path('admin_usuarios/<int:usuario_id>/', main_views.detalle_usuario, name='detalle_usuario'),
    path('admin_usuarios/<int:usuario_id>/eliminar/', main_views.eliminar_usuario, name='eliminar_usuario'),

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

    #esto es para que al usuario le pida el correo para recuperar la contraseña
    path('recuperar_contrasena/', 
         auth_views.PasswordResetView.as_view(
             template_name='taller/recuperar_contrasena.html'
         ), 
         name='password_reset'),

    # esto es para que se vea confirmado el envio del correo electronico    
    path('recuperar_contra_listo/', 
     auth_views.PasswordResetDoneView.as_view(
         template_name='taller/recuperar_contra_listo.html'
     ), 
     name='password_reset_done'),

     # Página con el formulario para poner la nueva contraseña
    path('nueva_contrasena/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='taller/nueva_contrasena.html'
         ), 
         name='password_reset_confirm'),

    #Pagina que permite al usuario saber que ha cambiado la contraseña

    path('contra_cambiada_exitosa/completado/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='taller/contra_cambiada_exitosa.html'  
         ), 
         name='password_reset_complete'),
    
    path('publicar_vehiculo', main_views.publicar_vehiculo, name='publicar_vehiculo'),
    path('estado_revi_vehiculos', main_views.estado_revi_vehiculos, name='estado_revi_vehiculos'),
    path('revisar_vehiculo', main_views.revisar_vehiculo, name='revisar_vehiculo'),
    path('aprobar_vehiculo/<int:id>/', main_views.aprobar_vehiculo, name='aprobar_vehiculo'),
    path('rechazar_vehiculo/<int:id>/', main_views.rechazar_vehiculo, name='rechazar_vehiculo'),
    path('carrito/json/', main_views.carrito_json, name='carrito_json'),
    path('carrito/actualizar/<int:item_id>/', main_views.carrito_actualizar, name='carrito_actualizar'),
    path('carrito/eliminar/<int:item_id>/', main_views.carrito_eliminar, name='carrito_eliminar'),

    path('custom_404', main_views.custom_404, name='custom_404'),

    

    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'Main.views.custom_404'
