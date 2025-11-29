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
    path('citas/<int:cita_id>/avanzar/', main_views.avanzar_estado_cita, name='avanzar_estado_cita'),
    path('mis_pedidos', main_views.mis_pedidos, name='mis_pedidos'),
    path('resumen_compra', main_views.resumen_compra, name='resumen_compra'),
    path('confirmacion_datos', main_views.confirmacion_datos, name='confirmacion_datos'),
    path('carrito_compras', main_views.carrito_compras, name='carrito_compras'),
    path('carrito/json/', main_views.carrito_json, name='carrito_json'),
    path('terminos', main_views.terminos, name='terminos'),
    path('privacidad', main_views.privacidad, name='privacidad'),
    path('agregar_editar', main_views.agregar_editar, name='agregar_editar'),
    path('agregar_editar/<int:pk>/editar/', main_views.agregar_editar, name='editar_producto'),
    path('crear_promocion/', main_views.crear_promocion, name='crear_promocion'),
    path('prueba', main_views.prueba, name='prueba'),
    path('compra_exitosa/', main_views.compra_exitosa, name='compra_exitosa'),
    path('compra_exitosa/<int:pedido_id>/', main_views.compra_exitosa, name='compra_exitosa_detalle'),
    path('compra_rechazada/', main_views.compra_rechazada, name='compra_rechazada'),
    path('compra_rechazada/<int:pedido_id>/', main_views.compra_rechazada, name='compra_rechazada'),
    path('ofertas', main_views.ofertas, name='ofertas'),
    path('retiro_despacho', main_views.retiro_despacho, name='retiro_despacho'),
    path('admin_agendamientos', main_views.admin_agendamientos, name='admin_agendamiento'),
    path('admin_configuracion', main_views.admin_configuracion, name='admin_configuracion'),
    path('admin_asignacion', main_views.admin_asignacion, name='admin_asignacion'),
    path('admin_pedidos', main_views.admin_pedidos, name='admin_pedidos'),
    path('asignar_pedidos', main_views.asignar_pedidos, name='asignar_pedidos'),
    path('admin_usuarios', main_views.admin_usuarios, name='admin_usuarios'),
    path('admin_usuarios/<int:usuario_id>/', main_views.detalle_usuario, name='detalle_usuario'),
    path('admin_usuarios/<int:usuario_id>/eliminar/', main_views.eliminar_usuario, name='eliminar_usuario'),
    path('admin_usuarios/bloquear/<int:user_id>/', main_views.toggle_bloqueo_usuario, name='toggle_bloqueo_usuario'),
    path('admin_entregas/', main_views.entregas_view, name='admin_entregas'),
    path("pedidos/<int:pedido_id>/estado/<str:nuevo_estado>/", main_views.actualizar_estado_pedido, name="actualizar_estado_pedido"),
    path("admin_horarios/", main_views.admin_horarios, name="administrar_horarios"),



    path("estadisticas/", main_views.estadisticas_view, name="estadisticas"),
    path("estadisticas/descargar_excel/", main_views.descargar_excel_pedidos, name="descargar_excel_pedidos"),
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
    path("pagos/flow/debug_check/", pay_views.flow_debug_check, name="flow_debug_check"),

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
    
    # Vehículos en venta (marketplace)
    path('vehiculos_venta', main_views.vehiculos_venta, name='vehiculos_venta'),
    path('vehiculo/<int:vehiculo_id>/', main_views.vehiculo_detalle, name='vehiculo_detalle'),
    
    # Gestión de vehículos (usuario)
    path('publicar_vehiculo', main_views.publicar_vehiculo, name='publicar_vehiculo'),
    path('estado_revi_vehiculos', main_views.estado_revi_vehiculos, name='estado_revi_vehiculos'),
    
    # Gestión de vehículos (admin)
    path('revisar_vehiculo', main_views.revisar_vehiculo, name='revisar_vehiculo'),
    path('aprobar_vehiculo/<int:id>/', main_views.aprobar_vehiculo, name='aprobar_vehiculo'),
    path('rechazar_vehiculo/<int:id>/', main_views.rechazar_vehiculo, name='rechazar_vehiculo'),
    path('cambiar_estado_vehiculo/<int:vehiculo_id>/', main_views.cambiar_estado_vehiculo, name='cambiar_estado_vehiculo'),
    
    path('carrito/json/', main_views.carrito_json, name='carrito_json'),
    path('carrito/actualizar/<int:item_id>/', main_views.carrito_actualizar, name='carrito_actualizar'),
    path('carrito/eliminar/<int:item_id>/', main_views.carrito_eliminar, name='carrito_eliminar'),

    path('custom_404', main_views.custom_404, name='custom_404'),

    # Gestión de productos
    path('producto/<int:pk>/eliminar/', main_views.eliminar_producto, name='eliminar_producto'),

    # Códigos de descuento
    path('admin_codigos_descuento', main_views.gestionar_codigos_descuento, name='gestionar_codigos_descuento'),
    path('api/aplicar-codigo-descuento/', main_views.aplicar_codigo_descuento, name='aplicar_codigo_descuento'),
    path('api/crear-codigo-descuento/', main_views.crear_codigo_descuento, name='crear_codigo_descuento'),

    # Contacto
    path('contacto/', main_views.contacto, name='contacto'),
    path('admin_contactos', main_views.admin_contactos, name='admin_contactos'),
    path('api/contacto/<int:contacto_id>/marcar-leido/', main_views.marcar_contacto_leido, name='marcar_contacto_leido'),

    # Reseñas
    path('producto/<int:producto_id>/resena/', main_views.agregar_resena, name='agregar_resena'),
    path('resenas/', main_views.resenas, name='resenas'),
    path('admin_resenas', main_views.admin_resenas, name='admin_resenas'),
    path('api/resena/<int:resena_id>/aprobar/', main_views.aprobar_resena, name='aprobar_resena'),
    path('api/resena/<int:resena_id>/rechazar/', main_views.rechazar_resena, name='rechazar_resena'),
    path('api/testimonio/<int:testimonio_id>/aprobar/', main_views.aprobar_testimonio, name='aprobar_testimonio'),
    path('api/testimonio/<int:testimonio_id>/rechazar/', main_views.rechazar_testimonio, name='rechazar_testimonio'),

    # Galería Nosotros
    path('admin_galeria_nosotros', main_views.admin_galeria_nosotros, name='admin_galeria_nosotros'),
    path('api/foto-nosotros/<int:foto_id>/eliminar/', main_views.eliminar_foto_nosotros, name='eliminar_foto_nosotros'),

    # Vehículos y historial
    path('mis_vehiculos', main_views.mis_vehiculos, name='mis_vehiculos'),
    path('agregar_vehiculo', main_views.agregar_vehiculo, name='agregar_vehiculo'),
    path('admin_historial_servicios', main_views.admin_historial_servicios, name='admin_historial_servicios'),
    path('api/historial-servicio/<int:historial_id>/actualizar/', main_views.actualizar_historial_servicio, name='actualizar_historial_servicio'),

    # Switch vista
    path('toggle-vista-admin/', main_views.toggle_vista_admin, name='toggle_vista_admin'),
    # entrega
    path("entrega/<int:pedido_id>/confirmar/", main_views.confirmar_entrega, name="confirmar_entrega"),

    # Horas disponibles (AJAX)
    path('api/horarios/crear-disponible/', main_views.crear_hora_disponible, name='crear_hora_disponible'),
    path('api/horarios/eliminar-disponible/', main_views.eliminar_hora_disponible, name='eliminar_hora_disponible'),
    path('api/horarios/listar-disponibles/', main_views.listar_horas_disponibles, name='listar_horas_disponibles'),
    path('api/horarios/bloques-por-fecha/', main_views.api_generar_bloques_por_fecha, name='api_bloques_por_fecha'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'Main.views.custom_404'
