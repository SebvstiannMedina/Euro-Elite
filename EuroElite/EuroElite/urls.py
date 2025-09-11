"""
URL configuration for EuroElite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from Main import views

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
    path('notfound', views.notfound, name='notfound'),
    path('agendar', views.agendar_cita, name='agendar'),
    path('nueva_contrasena', views.nueva_contrasena, name='nueva_contrasena'),
    path('mis_pedidos', views.mis_pedidos, name='mis_pedidos'),
    path('pago', views.pago, name='pago'),
    path('carrito_compras', views.carrito_compras, name='carrito_compras'),
    path('terminos', views.terminos, name='terminos'),
    path('privacidad', views.privacidad, name='privacidad'),
    path('agregar_editar', views.agregar_editar, name='agregar_editar'), 
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
]
