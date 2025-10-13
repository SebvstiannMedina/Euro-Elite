from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.dispatch import receiver
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from analytics.utils import track
from .forms import CitaForm, ProductoForm
from .models import Cita, Producto, BloqueHorario

# Local apps
from .forms import CitaForm, DireccionForm, PerfilForm, RegistroForm, EmailLoginForm
from .models import (Carrito,Categoria,ConfigSitio,Direccion,ItemCarrito,ItemPedido,Pago,Pedido,Producto,)

#temportal -- borrar despues
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Cita

from .forms import CitaForm
from .models import Cita, BloqueHorario

def _get_active_cart(user):
    """Devuelve (o crea) el carrito activo del usuario."""
    cart, _ = Carrito.objects.get_or_create(usuario=user, activo=True)
    return cart


# ---------- Endpoints de carrito (server) ----------
@login_required
@require_POST
def cart_add(request):
    prod_id = request.POST.get('producto_id')
    try:
        qty = int(request.POST.get('cantidad', 1))
    except (TypeError, ValueError):
        qty = 1

    if not prod_id or qty <= 0:
        return HttpResponseBadRequest("Datos inválidos.")

    producto = get_object_or_404(Producto, id=prod_id)
    cart = _get_active_cart(request.user)

    item, created = ItemCarrito.objects.get_or_create(
        carrito=cart, producto=producto,
        defaults={'cantidad': qty, 'precio_unitario': producto.precio}
    )
    if not created:
        item.cantidad += qty
        item.precio_unitario = producto.precio  # asegura precio vigente
        item.save(update_fields=['cantidad', 'precio_unitario'])

    # Cantidad total de ítems
    total_items = sum(i.cantidad for i in cart.items.all())
    track(request, "add_to_cart", product_id=producto.id, qty=qty)
    return JsonResponse({"ok": True, "items": total_items})


@login_required
@require_POST
def cart_update(request):
    item_id = request.POST.get('item_id')
    try:
        qty = int(request.POST.get('cantidad', 1))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Cantidad inválida.")

    if not item_id or qty < 0:
        return HttpResponseBadRequest("Datos inválidos.")

    cart = _get_active_cart(request.user)
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=cart)

    if qty == 0:
        item.delete()
    else:
        item.cantidad = qty
        item.save(update_fields=['cantidad'])

    return JsonResponse({"ok": True})


@login_required
@require_POST
def cart_remove(request):
    item_id = request.POST.get('item_id')
    if not item_id:
        return HttpResponseBadRequest("Falta item_id.")

    cart = _get_active_cart(request.user)
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=cart)
    item.delete()
    track(request, "remove_from_cart", item_id=item.id, product_id=item.producto.id)  # ← ANALYTICS
    return JsonResponse({"ok": True})


@login_required
def cart_json(request):
    """Devuelve el carrito en JSON para render del front."""
    cart = _get_active_cart(request.user)
    data = []
    for it in cart.items.select_related('producto'):
        data.append({
            "item_id": it.id,
            "producto_id": it.producto.id,
            "nombre": it.producto.nombre,
            "precio": float(it.precio_unitario),
            "cantidad": it.cantidad,
            "subtotal": float(it.precio_unitario * it.cantidad),
        })
    total = sum(d["subtotal"] for d in data)
    total_items = sum(d["cantidad"] for d in data)
    return JsonResponse({"items": data, "total": total, "count": total_items})


# ---------- Checkout ----------
@login_required
@require_POST 
@transaction.atomic
def checkout_crear_pedido_y_pagar(request):
    """
    1) Toma el carrito activo con ítems
    2) Crea Pedido + ItemPedido + Pago(PENDIENTE)
    3) Desactiva el carrito
    4) Redirige a payments:flow_crear_orden con ?pedido_id=...
    """
    cart = Carrito.objects.filter(usuario=request.user, activo=True).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect('carrito_compras')

    addr = Direccion.objects.filter(usuario=request.user).order_by('-predeterminada', '-id').first()

    # Crea Pedido
    pedido = Pedido.objects.create(
        usuario=request.user,
        estado=Pedido.Estado.PENDIENTE,
        metodo_entrega=Pedido.MetodoEntrega.DESPACHO,
        metodo_pago=Pedido.MetodoPago.PASARELA,
        direccion_envio=addr,
        direccion_facturacion=addr,
        subtotal=0, descuento=0, envio=0, total=0,
    )

    subtotal = 0
    for it in cart.items.select_related('producto'):
        ItemPedido.objects.create(
            pedido=pedido,
            producto=it.producto,
            nombre_producto=it.producto.nombre,
            sku_producto=it.producto.sku,
            precio_unitario=it.precio_unitario,
            cantidad=it.cantidad,
        )
        subtotal += it.precio_unitario * it.cantidad

        if it.producto.stock is not None:
            it.producto.stock = max(0, it.producto.stock - it.cantidad)
            it.producto.save(update_fields=['stock'])

    # Totales
    pedido.subtotal = subtotal
    pedido.envio = 0
    pedido.descuento = 0
    pedido.total = subtotal + pedido.envio - pedido.descuento
    pedido.save()

    # Pago PENDIENTE
    Pago.objects.create(
        pedido=pedido,
        metodo=Pedido.MetodoPago.PASARELA,
        monto=pedido.total,
        estado=Pago.Estado.PENDIENTE,
    )

    # Cerrar carrito
    cart.activo = False
    cart.save(update_fields=['activo'])
    track(request, "purchase", order_id=pedido.id, total=int(pedido.total))  # ← ANALYTICS
    # Redirigir a Flow
    pay_url = reverse("flow_crear_orden")
    return redirect(f"{pay_url}?pedido_id={pedido.id}")

# ========== PÁGINAS PÚBLICAS ==========
@ensure_csrf_cookie
def home(request):
    ahora = timezone.now()

    productos_oferta = (
        Producto.objects.filter(
            activo=True,
            promociones__activa=True,
        )
        .filter(Q(promociones__inicio__isnull=True) | Q(promociones__inicio__lte=ahora))
        .filter(Q(promociones__fin__isnull=True) | Q(promociones__fin__gte=ahora))
        .select_related('categoria')
        .distinct()
        .order_by('-id')[:6]
    )

    productos_normales = (
        Producto.objects.filter(activo=True)
        .exclude(id__in=productos_oferta.values('id'))
        .select_related('categoria')
        .order_by('-id')[:6]
    )

    return render(request, 'Taller/main.html', {
        'productos_oferta': productos_oferta,
        'productos_normales': productos_normales,
    })

def producto_detalle(request, pk):
    p = get_object_or_404(
        Producto.objects.select_related('categoria'),
        pk=pk,
        activo=True
    )
    track(request, "view_product", product_id=p.id)
    return render(request, 'Taller/producto_detalle.html', {'p': p})

def nosotros(request):
    return render(request, 'Taller/nosotros.html')

def equipo(request):
    return render(request, 'Taller/equipo.html')

def productos(request):
    productos = Producto.objects.filter(activo=True).select_related("categoria")
    categorias = Categoria.objects.filter(activa=True)

    for p in productos:
        p.promocion = p.promocion_vigente
        p.precio_descuento = p.precio_con_descuento

    return render(request, "Taller/productos.html", {
        "productos": productos,
        "categorias": categorias,
    })


# ========== LOGIN ==========
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import EmailAuthenticationForm
from .forms import RegistroForm
from django.shortcuts import render, redirect

class CustomLoginView(LoginView):
    template_name = "Taller/login.html"
    authentication_form = EmailAuthenticationForm

    def form_valid(self, form):
        messages.success(self.request, f"Bienvenido: {form.get_user().first_name or form.get_user().email}")
        track(self.request, "login", user_id=form.get_user().id)  # ← ANALYTICS
        return super().form_valid(form)

# ============ LOGOUT ============
class CustomLogoutView(LogoutView):
    next_page = "login"
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
            
            print("Errores del formulario:", form.errors)
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()

    return render(request, 'Taller/registro.html', {'form': form})

# ========== PERFIL ==========

@login_required
def perfil(request):
    usuario = request.user
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


#Vistas de agenda
@login_required
def agendar(request):
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    bloque_id = form.cleaned_data["bloque"].id

                    # 1) Lock a nivel fila:
                    bloque = (
                        BloqueHorario.objects
                        .select_for_update()
                        .get(id=bloque_id)
                    )

                    # 2) Doble chequeo con el lock tomado:
                    if bloque.bloqueado or Cita.objects.filter(bloque=bloque).exists():
                        form.add_error("bloque", "Este bloque ya está reservado.")
                        raise ValueError("Bloque ya reservado")

                    # 3) Crear la cita (única por bloque):
                    cita = Cita(
                        usuario=request.user,
                        servicio=form.cleaned_data["servicio"],
                        bloque=bloque,
                        estado=Cita.Estado.RESERVADA,
                        a_domicilio=form.cleaned_data.get("a_domicilio", False),
                        direccion_domicilio=form.cleaned_data.get("direccion_domicilio", ""),
                    )
                    cita.save()

                    # 4) Marcar bloque como ocupado:
                    bloque.bloqueado = True
                    bloque.save(update_fields=["bloqueado"])

            except ValueError:
                # Ya añadimos error en el form; seguimos mostrando el form.
                pass
            except IntegrityError:
                # Por si, a pesar del lock, colisiona la unicidad:
                form.add_error("bloque", "Este bloque ya está reservado.")
            else:
                messages.success(request, "Tu cita fue reservada correctamente ✅")
                return redirect("mis_citas")
    else:
        form = CitaForm()

    return render(request, "taller/agendar.html", {"form": form})

@login_required
def mis_citas(request):
    citas = (
        Cita.objects
        .filter(usuario=request.user)
        .select_related("servicio", "bloque")
        .order_by("bloque__inicio")
    )
    return render(request, "taller/mis_citas.html", {"citas": citas})


@login_required
def anular_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, usuario=request.user)

    if cita.estado == Cita.Estado.RESERVADA:
        cita.estado = Cita.Estado.CANCELADA
        cita.bloque.bloqueado = False
        cita.bloque.save()
        cita.save()
        messages.success(request, "La cita fue cancelada correctamente ❌")
    else:
        messages.warning(request, "Solo puedes cancelar citas que estén reservadas.")

    return redirect("mis_citas")


def nueva_contrasena(request):
    return render(request, 'Taller/nueva_contrasena.html')

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
    if pk:  # Editar producto
        producto = get_object_or_404(Producto, pk=pk)
    else:   # Agregar producto
        producto = None

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()
            messages.success(request, 'Producto guardado correctamente.')
            # 
            if pk:
                return redirect('editar_producto', pk=producto.pk)
           
            return redirect('agregar_editar')
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

from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def admin_agendamientos(request):
    citas = Cita.objects.all().order_by('-bloque__inicio')

    return render(request, 'Taller/admin_agendamientos.html', {'citas': citas})

def anular_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if cita.estado == "RESERVADA":
        cita.estado = "CANCELADA"
        cita.save()
        messages.success(request, "La cita fue cancelada correctamente.")
    return redirect("mis_citas")

def admin_configuracion(request):
    return render(request, 'Taller/admin_configuracion.html')

def admin_dashboard(request):
    return render(request, 'Taller/admin_agendamientos.html')

def admin_pedidos(request):
    return render(request, 'Taller/admin_agendamientos.html')

def admin_reportes(request):
    return render(request, 'Taller/admin_reportes.html')

from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required

Usuario = get_user_model()  # tu modelo custom de usuario

# Listar usuarios
@staff_member_required
def admin_usuarios(request):
    usuarios = Usuario.objects.all().order_by('-date_joined')
    return render(request, 'Taller/admin_usuarios.html', {"usuarios": usuarios})

# Detalle de un usuario
@staff_member_required
def detalle_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'Taller/detalle_usuario.html', {"usuario": usuario})

# Eliminar un usuario
@staff_member_required
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if usuario.is_superuser:
        messages.error(request, "No puedes eliminar a un superusuario.")
    else:
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
    return redirect("admin_usuarios")



def mis_pedidos(request):
    pedidos_qs = request.user.pedidos.all().order_by('-creado') if request.user.is_authenticated else []
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

        if telefono:
            user.telefono = telefono
        if rut:
            user.rut = rut
        user.save(update_fields=['telefono', 'rut'])

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

        request.session['checkout_rut'] = rut

        return redirect('pago')

    return render(request, 'Taller/confirmacion_datos.html', {
        'rut': rut,
        'addr': addr,
        'user': user,
    })

def olvide_contra(request):
    return render(request, 'Taller/olvide_contra.html')

def estadistica(request):
    labels = ["Enero 2025", "Febrero 2025", "Marzo 2025"]
    values = [220000, 330000, 200000]

    # Cálculos previos
    total = sum(values) if values else 0
    max_val = max(values) if values else 0
    mes_max = labels[values.index(max_val)] if values else "N/A"
    cantidad_pedidos = len(values)

    return render(request, "Taller/estadistica.html", {
        "labels": labels,
        "values": values,
        "total": total,
        "mes_max": mes_max,
        "cantidad_pedidos": cantidad_pedidos,
    })

def custom_404(request, exception):
    return render(request, 'Taller/notfound.html')

def _get_or_create_cart(request):
    # Asegura que exista una sesión
    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        cart, _ = Carrito.objects.get_or_create(usuario=request.user, activo=True)
        ses_cart = Carrito.objects.filter(clave_sesion=request.session.session_key, activo=True).first()
        if ses_cart and ses_cart != cart:
            for it in ses_cart.items.select_related('producto'):
                tgt, _ = ItemCarrito.objects.get_or_create(
                    carrito=cart, producto=it.producto,
                    defaults={'cantidad': 0, 'precio_unitario': it.precio_unitario}
                )
                tgt.cantidad += it.cantidad
                tgt.precio_unitario = it.precio_unitario
                tgt.save()
            ses_cart.activo = False
            ses_cart.save()
        return cart
    cart, _ = Carrito.objects.get_or_create(clave_sesion=request.session.session_key, activo=True)
    return cart


@require_POST
def api_cart_add(request):
    import json
    data = json.loads(request.body.decode('utf-8'))
    product_id = int(data.get('product_id'))
    quantity = max(1, int(data.get('quantity', 1)))

    p = get_object_or_404(Producto, pk=product_id, activo=True)
    cart = _get_or_create_cart(request)

    item, _ = ItemCarrito.objects.get_or_create(
        carrito=cart, producto=p,
        defaults={'cantidad': 0, 'precio_unitario': p.precio_con_descuento}
    )

    # Respeta stock
    if p.stock is not None:
        new_qty = min(item.cantidad + quantity, p.stock)
    else:
        new_qty = item.cantidad + quantity

    if new_qty == item.cantidad:
        return JsonResponse({"ok": False, "error": "Sin stock"}, status=400)

    item.cantidad = new_qty
    # Congela precio al momento
    item.precio_unitario = p.precio_con_descuento
    item.save()
    track(request, "add_to_cart", product_id=p.id, qty=quantity)
    count = cart.items.aggregate(total=Sum('cantidad'))['total'] or 0
    return JsonResponse({"ok": True, "count": count})


def api_cart_count(request):
    cart = _get_or_create_cart(request)
    count = cart.items.aggregate(total=Sum('cantidad'))['total'] or 0
    return JsonResponse({"count": count})


def api_cart_detail(request):
    cart = _get_or_create_cart(request)
    items = []
    for it in cart.items.select_related('producto'):
        items.append({
            "id": it.producto.id,
            "name": it.producto.nombre,
            "price": float(it.precio_unitario),
            "quantity": it.cantidad,
            "stock": it.producto.stock,
            "image": it.producto.imagen.url if it.producto.imagen else None,
        })
    total = sum(i["price"] * i["quantity"] for i in items)
    return JsonResponse({"items": items, "total": total})


@receiver(user_logged_in)
def _merge_on_login(sender, user, request, **kwargs):
    _get_or_create_cart(request)


def recuperar_contrasena(request):
    return render(request, 'Taller/recuperar_contrasena.html')

def recuperar_contra_listo(request):
    return render(request, 'Taller/recuperar_contra_listo.html')

def contra_cambiada_exitosa(request):
    return render(request, 'Taller/contra_cambiada_exitosa.html')

from django.contrib.auth.views import LoginView
from .forms import EmailAuthenticationForm

class CustomLoginView(LoginView):
    template_name = "Taller/login.html"
    authentication_form = EmailAuthenticationForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import VehiculoEnVenta
from .forms import VehiculoForm



@login_required
def publicar_vehiculo(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.usuario = request.user
            vehiculo.save()
            messages.success(request, "Tu vehículo fue enviado para aprobación del administrador.")
            return redirect('estado_revi_vehiculo')
        else:
            messages.error(request, "Por favor revisa los campos del formulario.")
    else:
        form = VehiculoForm()

    return render(request, 'taller/publicar_vehiculo.html', {'form': form})


# 🔹 Ver estado del usuario
@login_required
def estado_revi_vehiculos(request):
    vehiculos = VehiculoEnVenta.objects.filter(usuario=request.user)
    return render(request, 'taller/estado_revi_vehiculos.html', {'vehiculos': vehiculos})


# 🔹 Revisión por parte del administrador
@staff_member_required
def revisar_vehiculo(request):
    pendientes = VehiculoEnVenta.objects.filter(estado='pendiente')
    aprobados = VehiculoEnVenta.objects.filter(estado='aprobado')
    return render(request, 'taller/revisar_vehiculo.html', {
        'pendientes': pendientes,
        'aprobados': aprobados
    })


# 🔹 Aprobar o rechazar vehículo
@staff_member_required
def aprobar_vehiculo(request, id):
    vehiculo = get_object_or_404(VehiculoEnVenta, id=id)
    vehiculo.estado = 'aprobado'
    vehiculo.save()
    messages.success(request, f"Vehículo {vehiculo.marca} {vehiculo.modelo} aprobado correctamente.")
    return redirect('revisar_vehiculo')


@staff_member_required
def rechazar_vehiculo(request, id):
    vehiculo = get_object_or_404(VehiculoEnVenta, id=id)
    vehiculo.estado = 'rechazado'
    vehiculo.save()
    messages.error(request, f"Vehículo {vehiculo.marca} {vehiculo.modelo} fue rechazado.")
    return redirect('revisar_vehiculo')