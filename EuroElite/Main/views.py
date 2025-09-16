from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegistroForm, CitaForm, PerfilForm, DireccionForm
from .models import Producto
from .models import Direccion
from .models import ConfigSitio

# ========== PÁGINAS PÚBLICAS ==========
def home(request):
    return render(request, 'Taller/main.html')

def contacto(request):
    return render(request, 'Taller/contacto.html')

def equipo(request):
    return render(request, 'Taller/equipo.html')

def productos(request):
    productos = Producto.objects.filter(activo=True)
    for p in productos:
        p.promocion = p.promocion_vigente
        p.precio_descuento = p.precio_con_descuento
    return render(request, 'Taller/productos.html', {'productos': productos})


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
    usuario = request.user
    # Buscar la dirección más reciente del usuario
    addr = Direccion.objects.filter(usuario=usuario).order_by('-predeterminada', '-id').first()

    if request.method == "POST":
        perfil_form = PerfilForm(request.POST, instance=usuario)
        direccion_form = DireccionForm(request.POST, instance=addr)

        if perfil_form.is_valid() and direccion_form.is_valid():
            perfil_form.save()

            direccion = direccion_form.save(commit=False)
            direccion.usuario = usuario
            direccion.save()

            messages.success(request, "Perfil actualizado correctamente ✅")
            return redirect("perfil")
    else:
        perfil_form = PerfilForm(instance=usuario)
        direccion_form = DireccionForm(instance=addr)

    return render(request, "Taller/perfil.html", {
        "form": perfil_form,
        "direccion_form": direccion_form,
        "user": usuario,
        "addr": addr,
    })

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
    citas = request.user.citas.select_related('bloque').order_by('-bloque__inicio')
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

from .forms import ProductoForm
from .models import Producto

@login_required
def agregar_editar(request, pk=None):
    if pk:  # editar
        producto = Producto.objects.get(pk=pk)
    else:   # agregar
        producto = None

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto guardado correctamente.')
            return redirect('agregar_editar')  # puedes redirigir a otra vista si quieres
    else:
        form = ProductoForm(instance=producto)

    productos = Producto.objects.all().order_by('-id')
    return render(request, 'Taller/agregar_editar.html', {
        'form': form,
        'productos': productos,
        'editando': producto is not None
    })


def prueba(request):
    return render(request, 'Taller/prueba.html')

def compra_exitosa(request):
    return render(request, 'Taller/compra_exitosa.html')

def ofertas(request):
    return render(request, 'Taller/ofertas.html')

def retiro_despacho(request):
    return render(request, 'Taller/retiro_despacho.html')

def admin_agendamientos(request):
    return render(request, 'Taller/admin_agendamientos.html')

def admin_configuracion(request):
    return render(request, 'Taller/admin_agendamientos.html')

def admin_dashboard(request):
    return render(request, 'Taller/admin_agendamientos.html')

def admin_pedidos(request):
    return render(request, 'Taller/admin_agendamientos.html')

def admin_reportes(request):
    return render(request, 'Taller/admin_agendamientos.html')

def admin_usuarios(request):
    return render(request, 'Taller/admin_agendamientos.html')





# Sobrescribe la vista para ordenar pedidos por fecha de compra (desc)
def mis_pedidos(request):
    pedidos_qs = request.user.pedidos.all().order_by('-creado') if request.user.is_authenticated else []
    # La plantilla usa `p.fecha` para agrupar por da; proveemos ese alias
    pedidos = [
        {
            'fecha': p.creado,
            'estado': p.get_estado_display() if hasattr(p, 'get_estado_display') else '',
        }
        for p in pedidos_qs
    ]
    return render(request, 'Taller/mis_pedidos.html', {
        'pedidos': pedidos,
        'DEBUG': settings.DEBUG,
    })


def resumen_compra(request):
    shipping_cost = 4990
    try:
        cfg = ConfigSitio.objects.first()
        if cfg and cfg.costo_envio_base is not None:
            shipping_cost = int(cfg.costo_envio_base)
    except Exception:
        pass
    return render(request, 'Taller/resumen_compra.html', {
        'shipping_cost': shipping_cost,
    })


from django.contrib.auth.decorators import login_required
@login_required
def confirmacion_datos(request):
    user = request.user
    rut = request.session.get('checkout_rut', '')
    addr = Direccion.objects.filter(usuario=user).order_by('-predeterminada', '-id').first()

    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        nombre_completo = request.POST.get('nombre_completo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion_txt = request.POST.get('direccion', '').strip()

        # Guarda datos bsicos del usuario
        if telefono:
            user.telefono = telefono
            user.save(update_fields=['telefono'])

        # Guarda/actualiza direccin de envo predeterminada
        if not addr:
            addr = Direccion(usuario=user, tipo=Direccion.Tipo.ENVIO)
        if nombre_completo:
            addr.nombre_completo = nombre_completo
        if telefono:
            addr.telefono = telefono
        if direccion_txt:
            addr.linea1 = direccion_txt
        if not addr.ciudad:
            addr.ciudad = 'Santiago'
        addr.predeterminada = True
        addr.save()

        # Rut en sesin para el checkout
        request.session['checkout_rut'] = rut

        # Luego de guardar, continuar al siguiente paso (pago)
        return redirect('pago')

    return render(request, 'Taller/confirmacion_datos.html', {
        'rut': rut,
        'addr': addr,
        'user': user,
    })

def olvide_contra(request):
    return render(request, 'Taller/olvide_contra.html')