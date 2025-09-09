from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistroForm
from .forms import CitaForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PerfilForm
from .models import Perfil
# ========== PÁGINAS PÚBLICAS ==========
def home(request):
    return render(request, 'Taller/main.html')

def contacto(request):
    return render(request, 'Taller/contacto.html')

def equipo(request):
    return render(request, 'Taller/equipo.html')

def productos(request):
    return render(request, 'Taller/productos.html')


# ========== LOGIN ==========
def login(request):
    if request.user.is_authenticated:
        return redirect('perfil')  # Redirige si ya está logueado

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()

    return render(request, 'Taller/login.html', {'form': form})


# ========== REGISTRO ==========
def registro(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirige si ya está logueado

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro exitoso. Inicia sesión para continuar.')
            return redirect('login')
    else:
        form = RegistroForm()

    return render(request, 'Taller/registro.html', {'form': form})


# ========== PERFIL ==========

@login_required
def perfil(request):
    perfil, created = Perfil.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil')  # recarga la página con los datos actualizados
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'Taller/perfil.html', {'form': form, 'user': request.user})


# ========== LOGOUT ==========
@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('home')

def notfound(request):
    return render(request, 'Taller/notfound.html')

#Vistas de agenda#
@login_required
def agendar_cita(request):
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.usuario = request.user
            cita.save()
            return redirect('mis_citas')  # Redirige al historial del usuario
    else:
        form = CitaForm()
    return render(request, 'Taller/agendar.html', {'form': form})

@login_required
def mis_citas(request):
    citas = request.user.cita_set.all().order_by('-fecha', '-hora')
    return render(request, 'Taller/mis_citas.html', {'citas': citas})


def nueva_contrasena(request):
    return render(request, 'Taller/nueva_contrasena.html')

def mis_pedidos(request):
    # En esta primera versión solo renderiza la plantilla.
    # Cuando tengas el modelo listo, pasa la lista `pedidos` en el contexto.
    return render(request, 'Taller/mis_pedidos.html')

def pago(request):
    return render(request, 'Taller/pago.html')

def carrito_compras(request):
    return render(request, 'Taller/carrito_compras.html')

def terminos(request):
    return render(request, 'Taller/terminos.html')

def privacidad(request):
    return render(request, 'Taller/privacidad.html')