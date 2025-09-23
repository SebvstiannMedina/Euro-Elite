from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from Main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('contacto', views.contacto, name='contacto'),
    path('equipo', views.equipo, name='equipo'),
    path('productos', views.productos, name='productos'),
    path('perfil', views.perfil, name='perfil'),
    path('registro', views.registro, name='registro'),
    path('login', views.login, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('custom_404', views.custom_404, name='custom_404'),
    path('agendar', views.agendar_cita, name='agendar'),
    path('mis_citas', views.mis_citas, name='mis_citas'),
    path('nueva_contrasena', views.nueva_contrasena, name='nueva_contrasena'),
    path('mis_pedidos', views.mis_pedidos, name='mis_pedidos'),
    path('resumen_compra', views.resumen_compra, name='resumen_compra'),
    path('confirmacion_datos', views.confirmacion_datos, name='confirmacion_datos'),
    path('pago', views.pago, name='pago'),
    path('carrito_compras', views.carrito_compras, name='carrito_compras'),
    path('terminos', views.terminos, name='terminos'),
    path('privacidad', views.privacidad, name='privacidad'),
    path('agregar_editar', views.agregar_editar, name='agregar_editar'), 
    path('agregar_editar', views.agregar_editar, name='agregar_editar'),
    path('agregar_editar/<int:pk>/editar/', views.agregar_editar, name='editar_producto'),
    path('prueba', views.prueba, name='prueba'),   
    path('compra_exitosa', views.compra_exitosa, name='compra_exitosa'),
    path('ofertas', views.ofertas, name='ofertas'),   
    path('retiro_despacho', views.retiro_despacho, name='retiro_despacho'),   
    path('admin_agendamientos', views.admin_agendamientos, name='admin_agendamiento'),   
    path('admin_configuracion', views.admin_configuracion, name='admin_configuracion'),   
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),   
    path('admin_pedidos', views.admin_pedidos, name='admin_pedidos'),     
    path('admin_reportes', views.admin_reportes, name='admin_reportes'), 
    path('admin_usuarios', views.admin_usuarios, name='admin_usuarios'),  
    path('estadistica', views.estadistica, name='estadistica'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'Main.views.custom_404'

