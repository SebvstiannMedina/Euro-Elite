from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.db.models import Q, Sum, F
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
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

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

    # Si no tiene stock definido, asumimos 0 para evitar exceso
    stock_disponible = producto.stock if producto.stock is not None else 0
    if stock_disponible <= 0:
        return JsonResponse({"ok": False, "msg": "Producto sin stock disponible."}, status=400)

    item, created = ItemCarrito.objects.get_or_create(
        carrito=cart,
        producto=producto,
        defaults={'cantidad': 0, 'precio_unitario': producto.precio}
    )

    # Calculamos nueva cantidad
    nueva_cantidad = item.cantidad + qty

    # Si supera el stock, lo dejamos en el máximo permitido
    if nueva_cantidad > stock_disponible:
        nueva_cantidad = stock_disponible

    # Si no cambia (ya está al máximo), avisamos al usuario
    if nueva_cantidad == item.cantidad:
        return JsonResponse({
            "ok": False,
            "msg": "Ya has agregado el máximo disponible de este producto."
        }, status=400)

    # Actualizamos cantidad y precio
    item.cantidad = nueva_cantidad
    item.precio_unitario = producto.precio
    item.save(update_fields=['cantidad', 'precio_unitario'])

    total_items = sum(i.cantidad for i in cart.items.all())
    return JsonResponse({
        "ok": True,
        "items": total_items,
        "msg": f"Producto agregado. Cantidad total: {item.cantidad}"
    })


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
        # Verificar stock disponible
        stock_disponible = item.producto.stock if item.producto.stock is not None else 0
        
        # Si se intenta agregar más del stock disponible, limitar al máximo
        if qty > stock_disponible:
            return JsonResponse({
                "ok": False,
                "msg": f"Solo hay {stock_disponible} unidades disponibles de este producto."
            }, status=400)
        
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

    # Leer método de entrega del formulario (envio | retiro)
    metodo_entrega_form = request.POST.get('metodo_entrega', 'envio').strip().lower()
    
    # Determinar método de entrega para el pedido
    if metodo_entrega_form == 'retiro':
        metodo_entrega = Pedido.MetodoEntrega.RETIRO
    else:
        metodo_entrega = Pedido.MetodoEntrega.DESPACHO

    # Crea Pedido
    pedido = Pedido.objects.create(
        usuario=request.user,
        estado=Pedido.Estado.PENDIENTE,
        metodo_entrega=metodo_entrega,
        metodo_pago=Pedido.MetodoPago.PASARELA,
        direccion_envio=addr,
        direccion_facturacion=addr,
        subtotal=0, descuento=0, envio=0, total=0,
    )

    subtotal = Decimal(0)
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

        # ⚠️ NO descontamos stock aquí - se descuenta solo cuando Flow confirma el pago

    # Calcular costo de envío según método elegido
    if metodo_entrega == Pedido.MetodoEntrega.RETIRO:
        envio_cost = Decimal(0)
    else:
        # Obtener costo de envío configurado (fallback 4990)
        envio_cost = Decimal(4990)
        try:
            cfg = ConfigSitio.objects.first()
            if cfg and getattr(cfg, 'costo_envio_base', None) is not None:
                envio_cost = Decimal(cfg.costo_envio_base)
        except Exception:
            pass

    # Totales
    pedido.subtotal = subtotal
    pedido.envio = envio_cost
    pedido.descuento = Decimal(0)
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
    
    # Guardar pedido_id en sesión para recuperarlo después del pago
    request.session['last_order_id'] = pedido.id
    request.session.modified = True
    request.session.save()  # Forzar guardado inmediato
    
    print(f"[CHECKOUT] Pedido {pedido.id} creado y guardado en sesión")
    print(f"[CHECKOUT] Session keys después de guardar: {list(request.session.keys())}")
    
    # Redirigir a Flow
    pay_url = reverse("flow_crear_orden")
    return redirect(f"{pay_url}?pedido_id={pedido.id}")

# ========== PÁGINAS PÚBLICAS ==========
@ensure_csrf_cookie
def home(request):
    ahora = timezone.now()

    # Filtrar productos que tengan stock mayor al mínimo (stock > stock_minimo)
    productos_oferta = (
        Producto.objects.filter(
            activo=True,
            promociones__activa=True,
        )
        .filter(Q(promociones__inicio__isnull=True) | Q(promociones__inicio__lte=ahora))
        .filter(Q(promociones__fin__isnull=True) | Q(promociones__fin__gte=ahora))
        .filter(stock__gt=F('stock_minimo'))  # Solo productos con stock > stock_minimo
        .select_related('categoria')
        .distinct()
        .order_by('-id')[:6]
    )

    productos_normales = (
        Producto.objects.filter(activo=True)
        .filter(stock__gt=F('stock_minimo'))  # Solo productos con stock > stock_minimo
        .exclude(id__in=productos_oferta.values('id'))
        .select_related('categoria')
        .order_by('-id')[:6]
    )

    return render(request, 'taller/main.html', {
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
    return render(request, 'taller/producto_detalle.html', {'p': p})

def nosotros(request):
    return render(request, 'taller/nosotros.html')

def equipo(request):
    return render(request, 'taller/equipo.html')

def productos(request):
    # Solo mostrar productos con stock > stock_minimo
    productos = Producto.objects.filter(activo=True).filter(stock__gt=F('stock_minimo')).select_related("categoria")
    categorias = Categoria.objects.filter(activa=True)

    for p in productos:
        p.promocion = p.promocion_vigente
        p.precio_descuento = p.precio_con_descuento

    return render(request, "taller/productos.html", {
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
    template_name = "taller/login.html"
    authentication_form = EmailAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()

        # Si el usuario está bloqueado, detener login
        if getattr(user, 'bloqueado', False):
            messages.error(
                self.request,
                "⚠️ Tu cuenta ha sido bloqueada por un administrador. "
                "Si crees que se trata de un error, contacta con el soporte de Euro Elite."
            )
            return redirect('login')

        # Login normal
        messages.success(self.request, f"Bienvenido: {user.first_name or user.email}")
        track(self.request, "login", user_id=user.id)
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Este método se ejecuta cuando el formulario NO es válido,
        es decir, cuando las credenciales son incorrectas o el backend
        rechazó al usuario bloqueado.
        """
        email = self.request.POST.get('username') or self.request.POST.get('email')

        from Main.models import Usuario  
        try:
            usuario = Usuario.objects.get(email=email)
            if usuario.bloqueado:
                messages.error(
                    self.request,
                    "⚠️ Tu cuenta ha sido bloqueada por un administrador. "
                    "No puedes iniciar sesión hasta que sea desbloqueada."
                )
                return redirect('login')
        except Usuario.DoesNotExist:
            pass

        # Si no está bloqueado, mostrar error estándar
        messages.error(self.request, "Correo o contraseña incorrectos.")
        return super().form_invalid(form)
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

    return render(request, 'taller/registro.html', {'form': form})

# ========== PERFIL ==========

@login_required
def perfil(request):
    usuario = request.user
    addr = Direccion.objects.filter(usuario=usuario).order_by('-predeterminada', '-id').first()

    if request.method == "POST":
        perfil_form = PerfilForm(request.POST, instance=usuario)
        direccion_form = DireccionForm(request.POST, instance=addr)

        if perfil_form.is_valid() and direccion_form.is_valid():
            # Guardar perfil del usuario
            perfil_form.save()

            # Guardar dirección (crear o actualizar)
            direccion = direccion_form.save(commit=False)
            direccion.usuario = usuario
            
            # Rellenar campos requeridos de Direccion desde Usuario
            direccion.nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip()
            direccion.telefono = usuario.telefono or ""
            
            # Si no hay dirección existente, marcar como predeterminada
            if not addr:
                direccion.predeterminada = True
            
            direccion.save()
            
            messages.success(request, "Perfil actualizado correctamente ✔")
            return redirect("perfil")
    else:
        perfil_form = PerfilForm(instance=usuario)
        
        # Si no existe dirección, crear un formulario vacío
        if addr:
            direccion_form = DireccionForm(instance=addr)
        else:
            direccion_form = DireccionForm()

    return render(request, "taller/perfil.html", {
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
    return render(request, 'taller/nueva_contrasena.html')

def pago(request):
    return render(request, 'taller/pago.html')

def carrito_compras(request):
    return render(request, 'taller/carrito_compras.html')

def terminos(request):
    return render(request, 'taller/terminos.html')

def privacidad(request):
    return render(request, 'taller/privacidad.html')

from .forms import ProductoForm
from .models import Producto
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
@login_required
@require_POST
def crear_promocion(request):
    """Crea una nueva promoción via AJAX"""
    try:
        from .models import Promocion
        from decimal import Decimal
        
        nombre = request.POST.get('nombre', '').strip()
        tipo = request.POST.get('tipo', 'PORCENTAJE')
        valor = request.POST.get('valor', '0')
        inicio = request.POST.get('inicio', None)
        fin = request.POST.get('fin', None)
        activa = request.POST.get('activa') == 'on'
        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
        
        if tipo not in ['PORCENTAJE', 'MONTO']:
            return JsonResponse({'success': False, 'error': 'Tipo de promoción inválido'})
        
        try:
            valor_decimal = Decimal(valor)
            if valor_decimal < 0:
                return JsonResponse({'success': False, 'error': 'El valor debe ser positivo'})
            if tipo == 'PORCENTAJE' and valor_decimal > 100:
                return JsonResponse({'success': False, 'error': 'El porcentaje no puede ser mayor a 100'})
        except:
            return JsonResponse({'success': False, 'error': 'Valor inválido'})
        
        # Convertir fechas
        inicio_dt = None
        fin_dt = None
        if inicio:
            try:
                from django.utils.dateparse import parse_datetime
                inicio_dt = parse_datetime(inicio)
            except:
                pass
        
        if fin:
            try:
                from django.utils.dateparse import parse_datetime
                fin_dt = parse_datetime(fin)
            except:
                pass
        
        # Crear promoción
        promocion = Promocion.objects.create(
            nombre=nombre,
            tipo=tipo,
            valor=valor_decimal,
            inicio=inicio_dt,
            fin=fin_dt,
            activa=activa
        )
        
        return JsonResponse({
            'success': True,
            'promocion': {
                'id': promocion.id,
                'nombre': promocion.nombre,
                'tipo': promocion.tipo,
                'valor': str(promocion.valor)
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@staff_member_required
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
    return render(request, 'taller/agregar_editar.html', {
        'form': form,
        'productos': productos,
        'editando': producto is not None
    })


def prueba(request):
    return render(request, 'taller/prueba.html')

@csrf_exempt
def compra_exitosa(request, pedido_id=None):
    """
    Muestra la página de compra exitosa con los detalles del pedido.
    PRIORIDAD: Encontrar el pedido primero, autenticación después.
    """
    print(f"[COMPRA_EXITOSA] ========== INICIO ==========")
    print(f"[COMPRA_EXITOSA] pedido_id recibido: {pedido_id}")
    print(f"[COMPRA_EXITOSA] Usuario autenticado: {request.user.is_authenticated}")
    print(f"[COMPRA_EXITOSA] User: {request.user}")
    print(f"[COMPRA_EXITOSA] Session keys: {list(request.session.keys())}")
    print(f"[COMPRA_EXITOSA] GET params: {dict(request.GET)}")
    
    pedido = None
    pago = None
    
    # PASO 1: Intentar obtener pedido_id de TODAS las fuentes posibles
    if not pedido_id:
        # Desde la sesión
        pedido_id = request.session.get('last_order_id')
        print(f"[COMPRA_EXITOSA] pedido_id desde sesión: {pedido_id}")
    
    # PASO 2: Intentar cargar el pedido (con o sin autenticación)
    if pedido_id:
        try:
            # Intentar cargar el pedido SIN filtrar por usuario
            pedido = Pedido.objects.select_related('usuario').prefetch_related('items__producto').get(id=pedido_id)
            pago = getattr(pedido, 'pago', None)
            print(f"[COMPRA_EXITOSA] ✅ Pedido {pedido.id} encontrado para usuario {pedido.usuario.email}")
            print(f"[COMPRA_EXITOSA] Estado del pedido: {pedido.estado}")
            
            if pedido.estado == Pedido.Estado.CANCELADO:
                print(f"[COMPRA_EXITOSA] 🚫 Pedido CANCELADO - redirigiendo a compra_rechazada")
                return redirect('compra_rechazada', pedido_id=pedido.id)
            
            # Guardar en sesión para futuras visitas
            request.session['last_order_id'] = pedido.id
            
        except Pedido.DoesNotExist:
            print(f"[COMPRA_EXITOSA] ❌ Pedido {pedido_id} NO existe en BD")
            pedido = None
    
    # PASO 3: Si NO hay pedido y el usuario está autenticado, buscar el más reciente
    if not pedido and request.user.is_authenticated:
        print(f"[COMPRA_EXITOSA] Buscando pedido más reciente para usuario autenticado")
        pedido = Pedido.objects.filter(
            usuario=request.user
        ).select_related('usuario').prefetch_related('items__producto').order_by('-creado').first()
        
        if pedido:
            pago = getattr(pedido, 'pago', None)
            print(f"[COMPRA_EXITOSA] ✅ Pedido más reciente encontrado: {pedido.id}")
    
    # PASO 4: Si AÚN no hay pedido, mostrar mensaje
    if not pedido:
        print(f"[COMPRA_EXITOSA] ⚠️ No se encontró ningún pedido")
        messages.info(request, "Tu pago está siendo procesado. Recibirás una confirmación por correo.")
    
    # PASO 5: Preparar contexto (funciona con o sin pedido)
    comprobante_url = pago.comprobante_url if pago and hasattr(pago, 'comprobante_url') else None
    numero_pedido = getattr(pedido, 'id', None) if pedido else None
    total = getattr(pedido, 'total', None) if pedido else None
    metodo_pago = getattr(pago, 'metodo', None) if pago else None
    
    # Usuario para el template (puede ser el del pedido o el autenticado)
    template_user = request.user if request.user.is_authenticated else (pedido.usuario if pedido else None)
    
    print(f"[COMPRA_EXITOSA] Renderizando template con pedido_id={numero_pedido}")
    print(f"[COMPRA_EXITOSA] ========== FIN ==========")
    
    return render(request, 'taller/compra_exitosa.html', {
        'user': template_user,
        'pedido': pedido,
        'numero_pedido': numero_pedido,
        'total': total,
        'metodo_pago': metodo_pago,
        'comprobante_url': comprobante_url,
    })


@csrf_exempt
def compra_rechazada(request, pedido_id=None):
    """
    Muestra la página de compra rechazada cuando el pago falla.
    """
    print(f"[COMPRA_RECHAZADA] ========== INICIO ==========")
    print(f"[COMPRA_RECHAZADA] pedido_id recibido: {pedido_id}")
    print(f"[COMPRA_RECHAZADA] Usuario autenticado: {request.user.is_authenticated}")
    
    pedido = None
    pago = None
    motivo_rechazo = None
    
    # Intentar obtener pedido_id de sesión si no se proporciona
    if not pedido_id:
        pedido_id = request.session.get('last_order_id')
        print(f"[COMPRA_RECHAZADA] pedido_id desde sesión: {pedido_id}")
    
    # Cargar el pedido
    if pedido_id:
        try:
            pedido = Pedido.objects.select_related('usuario').prefetch_related('items__producto').get(id=pedido_id)
            pago = getattr(pedido, 'pago', None)
            print(f"[COMPRA_RECHAZADA] ✅ Pedido {pedido.id} encontrado, estado: {pedido.estado}")
            
            # Intentar obtener el motivo del rechazo desde la respuesta de Flow
            if pago and hasattr(pago, 'flow_response') and pago.flow_response:
                try:
                    import json
                    flow_data = json.loads(pago.flow_response.replace("'", '"'))
                    last_error = flow_data.get('lastError', {})
                    if last_error and last_error.get('message'):
                        motivo_rechazo = last_error.get('message')
                except:
                    pass
                    
        except Pedido.DoesNotExist:
            print(f"[COMPRA_RECHAZADA] ❌ Pedido {pedido_id} NO existe")
    
    # Si no hay pedido y el usuario está autenticado, buscar el más reciente cancelado
    if not pedido and request.user.is_authenticated:
        pedido = Pedido.objects.filter(
            usuario=request.user,
            estado=Pedido.Estado.CANCELADO
        ).order_by('-creado').first()
        
        if pedido:
            pago = getattr(pedido, 'pago', None)
            print(f"[COMPRA_RECHAZADA] ✅ Pedido cancelado más reciente: {pedido.id}")
    
    numero_pedido = getattr(pedido, 'id', None) if pedido else None
    total = getattr(pedido, 'total', None) if pedido else None
    template_user = request.user if request.user.is_authenticated else (pedido.usuario if pedido else None)
    
    print(f"[COMPRA_RECHAZADA] Renderizando template con pedido_id={numero_pedido}")
    print(f"[COMPRA_RECHAZADA] ========== FIN ==========")
    
    return render(request, 'taller/compra_rechazada.html', {
        'user': template_user,
        'pedido': pedido,
        'numero_pedido': numero_pedido,
        'total': total,
        'motivo_rechazo': motivo_rechazo or 'El pago fue rechazado por el medio de pago.',
    })


def ofertas(request):
    return render(request, 'taller/ofertas.html')

def retiro_despacho(request):
    return render(request, 'taller/retiro_despacho.html')

from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def admin_agendamientos(request):
    citas = Cita.objects.all().order_by('-bloque__inicio')

    return render(request, 'taller/admin_agendamientos.html', {'citas': citas})

def anular_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if cita.estado == "RESERVADA":
        cita.estado = "CANCELADA"
        cita.save()
        messages.success(request, "La cita fue cancelada correctamente.")
    return redirect("mis_citas")

def admin_configuracion(request):
    return render(request, 'taller/admin_configuracion.html')

def admin_dashboard(request):
    return render(request, 'taller/admin_agendamientos.html')

@staff_member_required
def admin_pedidos(request):
    # Obtener todos los pedidos con sus relaciones necesarias
    pedidos = Pedido.objects.select_related(
        'usuario', 
        'direccion_envio',
        'pago'
    ).prefetch_related(
        'items__producto'
    ).order_by('-creado')
    
    # Agrupar pedidos por usuario para la vista
    from itertools import groupby
    pedidos_por_usuario = []
    
    # Agrupar por usuario.email
    for email, pedidos_grupo in groupby(pedidos, key=lambda p: p.usuario.email if p.usuario else 'Sin usuario'):
        pedidos_lista = list(pedidos_grupo)
        pedidos_por_usuario.append({
            'grouper': email,
            'list': pedidos_lista
        })
    
    return render(request, 'taller/admin_pedidos.html', {
        'pedidos': pedidos,
        'pedidos_por_usuario': pedidos_por_usuario,
    })

def admin_reportes(request):
    return render(request, 'taller/admin_reportes.html')

from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required

Usuario = get_user_model()  # tu modelo custom de usuario

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from .models import Usuario

@staff_member_required
def admin_usuarios(request):
    # Obtener parámetros de búsqueda
    q = request.GET.get('q', '')
    rol = request.GET.get('rol', '')

    # Base queryset (todos los usuarios)
    usuarios = Usuario.objects.all().order_by('-date_joined')

    # --- Filtro de búsqueda ---
    if q:
        usuarios = usuarios.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(username__icontains=q)
        )

    # --- Filtro por rol ---
    if rol:
        usuarios = usuarios.filter(rol=rol)

    # --- Paginación (20 por página) ---
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "usuarios": page_obj,  # importante: para que el HTML funcione igual
        "page_obj": page_obj,
        "q": q,
        "rol": rol,
    }

    return render(request, 'taller/admin_usuarios.html', context)



# Detalle de un usuario
@staff_member_required
def detalle_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'taller/detalle_usuario.html', {"usuario": usuario})

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
    if not request.user.is_authenticated:
        return redirect('login')
    
    pedidos_qs = request.user.pedidos.select_related('pago').prefetch_related('items__producto__imagenes').order_by('-creado')
    
    pedidos = []
    for p in pedidos_qs:
        # Obtener el primer item para mostrar la imagen principal
        primer_item = p.items.first()
        imagen_url = ''
        titulo = 'Detalle de compra'
        descripcion = ''
        cantidad_total = sum(item.cantidad for item in p.items.all())
        num_items_diferentes = p.items.count()
        
        if primer_item:
            # Imagen del primer producto - primero intentar la imagen directa del producto
            if primer_item.producto.imagen:
                imagen_url = primer_item.producto.imagen.url
            else:
                # Si no tiene imagen directa, buscar en las imágenes relacionadas
                primera_imagen = primer_item.producto.imagenes.first()
                if primera_imagen:
                    imagen_url = primera_imagen.imagen.url
            
            # Título y descripción
            if num_items_diferentes == 1:
                titulo = primer_item.nombre_producto
                descripcion = f"SKU: {primer_item.sku_producto}"
            else:
                titulo = f"{primer_item.nombre_producto} y {num_items_diferentes - 1} producto(s) más"
                descripcion = f"Pedido con {num_items_diferentes} productos"
        
        # Calcular fecha de entrega estimada (7 días después de creado si es despacho)
        fecha_entrega = None
        if p.metodo_entrega == Pedido.MetodoEntrega.DESPACHO and p.estado in [Pedido.Estado.PAGADO, Pedido.Estado.PREPARACION, Pedido.Estado.ENVIADO]:
            fecha_entrega = p.creado + timezone.timedelta(days=7)
        
        pedidos.append({
            'id': p.id,
            'fecha': p.creado,
            'fecha_entrega': fecha_entrega,
            'estado': p.get_estado_display(),
            'imagen_url': imagen_url,
            'titulo': titulo,
            'descripcion': descripcion,
            'cantidad': cantidad_total,
            'vendedor': 'Euro Elite',
            'detalle_url': reverse('compra_exitosa_detalle', args=[p.id]),
            'recomprar_url': None,  # Se puede implementar más adelante
        })
    
    return render(request, 'taller/mis_pedidos.html', {
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
    return render(request, 'taller/resumen_compra.html', {
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
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion_txt = request.POST.get('direccion', '').strip()
        direccion2_txt = request.POST.get('direccion2', '').strip()
        region = request.POST.get('region', '').strip()
        comuna = request.POST.get('comuna', '').strip()
        notas = request.POST.get('notas', '').strip()

        if nombre:
            user.first_name = nombre[:25] 
        if apellido:
            user.last_name = apellido[:25]
        if email:
            email_clean = email.replace(' ', '').lower()
            for char in ['<', '>', '"', "'", ';', '\r', '\n', '\t']:
                email_clean = email_clean.replace(char, '')
            if len(email_clean) <= 120:
                user.email = email_clean
        if telefono:
            telefono_digits = ''.join(filter(str.isdigit, telefono))
            if len(telefono_digits) == 8:
                user.telefono = telefono_digits
        if rut:
            user.rut = rut
        
        user.save(update_fields=['first_name', 'last_name', 'email', 'telefono', 'rut'])

        if not addr:
            addr = Direccion(usuario=user, tipo=Direccion.Tipo.ENVIO)
        
        if direccion_txt:
            addr.linea1 = direccion_txt[:65] 
        if direccion2_txt:
            addr.linea2 = direccion2_txt[:65]
        if telefono:
            telefono_digits = ''.join(filter(str.isdigit, telefono))
            if len(telefono_digits) == 8:
                addr.telefono = telefono_digits
        if region:
            addr.region = region
        if comuna:
            addr.comuna = comuna
        if not addr.ciudad:
            addr.ciudad = 'Santiago'
        
        addr.predeterminada = True
        addr.save()

        request.session['checkout_rut'] = rut

        return redirect('pago')

    try:
        cart = _get_active_cart(user)
    except Exception:
        cart = None

    subtotal_dec = Decimal(0)
    if cart:
        try:
            for it in cart.items.all():
                price = it.precio_unitario or Decimal(0)
                qty = int(getattr(it, 'cantidad', 0) or 0)
                subtotal_dec += (price * qty)
        except Exception:
            pass

    shipping_cost_int = 4990
    try:
        cfg = ConfigSitio.objects.first()
        if cfg and getattr(cfg, 'costo_envio_base', None) is not None:
            shipping_cost_int = int(cfg.costo_envio_base)
    except Exception:
        pass

    envio_dec = Decimal(shipping_cost_int)
    total_dec = (subtotal_dec or Decimal(0)) + envio_dec

    def _format_clp(amount: Decimal) -> str:
        try:
            return "$" + f"{int(amount):,}".replace(",", ".")
        except Exception:
            return "-"

    context = {
        'rut': rut,
        'addr': addr,
        'user': user,
        'subtotal': _format_clp(subtotal_dec),
        'envio': _format_clp(envio_dec),
        'total': _format_clp(total_dec),
    }

    return render(request, 'taller/confirmacion_datos.html', context)

def olvide_contra(request):
    return render(request, 'taller/olvide_contra.html')

def estadisticas(request):
    labels = ["Enero 2025", "Febrero 2025", "Marzo 2025"]
    values = [220000, 330000, 200000]

    # Cálculos previos
    total = sum(values) if values else 0
    max_val = max(values) if values else 0
    mes_max = labels[values.index(max_val)] if values else "N/A"
    cantidad_pedidos = len(values)

    return render(request, "taller/estadisticas.html", {
        "labels": labels,
        "values": values,
        "total": total,
        "mes_max": mes_max,
        "cantidad_pedidos": cantidad_pedidos,
    })

def custom_404(request, exception):
    return render(request, 'taller/notfound.html')

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
    return render(request, 'taller/recuperar_contrasena.html')

def recuperar_contra_listo(request):
    return render(request, 'taller/recuperar_contra_listo.html')

def contra_cambiada_exitosa(request):
    return render(request, 'taller/contra_cambiada_exitosa.html')

from django.contrib.auth.views import LoginView
from .forms import EmailAuthenticationForm

class CustomLoginView(LoginView):
    template_name = "taller/login.html"
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



@login_required
def estado_revi_vehiculos(request):
    vehiculos = VehiculoEnVenta.objects.filter(usuario=request.user)
    return render(request, 'taller/estado_revi_vehiculos.html', {'vehiculos': vehiculos})



@staff_member_required
def revisar_vehiculo(request):
    pendientes = VehiculoEnVenta.objects.filter(estado='pendiente')
    aprobados = VehiculoEnVenta.objects.filter(estado='aprobado')
    return render(request, 'taller/revisar_vehiculo.html', {
        'pendientes': pendientes,
        'aprobados': aprobados
    })



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

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Carrito, ItemCarrito

@login_required
def carrito_json(request):
    try:
        # Busca el carrito del usuario activo
        carrito = Carrito.objects.filter(usuario=request.user, activo=True).prefetch_related('items__producto').first()

        if not carrito:
            return JsonResponse({"items": [], "total": 0})

        items_data = []
        total = 0

        for item in carrito.items.all():
            subtotal = float(item.precio_unitario) * item.cantidad
            total += subtotal
            items_data.append({
                "item_id": item.id,
                "producto_id": item.producto.id,
                "nombre": item.producto.nombre,
                "precio": float(item.precio_unitario),
                "cantidad": item.cantidad,
                "subtotal": subtotal
            })

        return JsonResponse({"items": items_data, "total": total})

    except Exception as e:
        print("Error en carrito_json:", e)
        return JsonResponse({"items": [], "total": 0})

from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@require_POST
@login_required
def carrito_actualizar(request, item_id):
    item = get_object_or_404(
        ItemCarrito,
        id=item_id,
        carrito__usuario=request.user,
        carrito__activo=True
    )

   
    try:
        nueva_cantidad = int(request.POST.get("cantidad", 1))
    except (ValueError, TypeError):
        nueva_cantidad = 1

   
    if nueva_cantidad <= 0:
        item.delete()
        return JsonResponse({"ok": True, "msg": "Producto eliminado"})

   
    stock = getattr(item.producto, "stock", None)
    if stock and nueva_cantidad > stock:
        nueva_cantidad = stock

    
    item.cantidad = nueva_cantidad
    item.save(update_fields=["cantidad"])

   
    return JsonResponse({
        "ok": True,
        "msg": "Cantidad actualizada",
        "cantidad": item.cantidad,
        "subtotal": float(item.cantidad * item.precio_unitario)
    })



@require_POST
@login_required
def carrito_eliminar(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user, carrito__activo=True)
    item.delete()
    return JsonResponse({"ok": True, "msg": "Producto eliminado"})


# ============================= Bloquear usuario =============================

@staff_member_required
def toggle_bloqueo_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)

    # Evitar bloquear administradores o superusuarios
    if usuario.is_superuser or usuario.rol == Usuario.Rol.ADMIN:
        messages.warning(request, "No puedes bloquear a un usuario administrador.")
        return redirect('admin_usuarios')

    usuario.bloqueado = not usuario.bloqueado
    usuario.save()

    if usuario.bloqueado:
        messages.warning(request, f"El usuario {usuario.get_full_name() or usuario.email} ha sido bloqueado.")
    else:
        messages.success(request, f"El usuario {usuario.get_full_name() or usuario.email} ha sido desbloqueado.")

    return redirect('admin_usuarios')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Pedido

@staff_member_required
@login_required
def entregas_view(request):
    """
    Muestra los pedidos asignados al usuario.
    Si el usuario es superusuario, muestra todos los pedidos.
    """
    if request.user.is_superuser:
        pedidos = Pedido.objects.all().order_by('-creado')
    else:
        pedidos = Pedido.objects.filter(asignado_a=request.user).order_by('-creado')

    return render(request, 'taller/admin_entregas.html', {'pedidos': pedidos})

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Pedido

@staff_member_required
@login_required
def actualizar_estado_pedido(request, pedido_id, nuevo_estado):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if nuevo_estado == "ENTREGADO":
        pedido.marcar_como_entregado(request.user.get_full_name() or request.user.email)
        messages.success(request, f"✅ Pedido entregado por {pedido.entregado_por}.")
    elif nuevo_estado == "EN_RUTA":
        pedido.marcar_en_ruta()
        messages.info(request, "🚚 Pedido marcado como EN RUTA.")
    else:
        pedido.estado = nuevo_estado
        pedido.save()
        messages.info(request, f"📦 Pedido actualizado a {pedido.get_estado_display()}.")

    # Redirige dinámicamente a la página desde donde se hizo clic
    return redirect(request.META.get('HTTP_REFERER', 'admin_entregas'))

import pandas as pd
from django.http import HttpResponse
from django.db.models import Sum
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from .models import Pedido
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import Pedido

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from .models import Pedido


@staff_member_required
def descargar_excel_pedidos(request):
    pedidos = Pedido.objects.all().order_by("-creado")

  
    wb = Workbook()
    ws = wb.active
    ws.title = "Pedidos"

   
    headers = [
        "ID", "Cliente", "Estado", "Precio (Venta)",
        "Costo", "Total (Precio - Costo)", "IVA (19%)",
        "Método Entrega", "Método Pago", "Fecha", "Entregado por"
    ]
    ws.append(headers)

    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    border_style = Side(style="thin", color="D1D5DB")

    for col in ws.iter_cols(min_row=1, max_row=1, min_col=1, max_col=len(headers)):
        for cell in col:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = Border(top=border_style, bottom=border_style, left=border_style, right=border_style)

    # 📊 Variables para totales
    total_precio = 0
    total_costo = 0
    total_ganancia = 0
    total_iva = 0


    for p in pedidos:
        precio = float(p.total or 0)
        costo = round(precio * 0.75, 0)  # estimación de costo
        total = precio - costo
        iva = round(precio * 0.19, 0)

        total_precio += precio
        total_costo += costo
        total_ganancia += total
        total_iva += iva

        ws.append([
            p.id,
            p.usuario.get_full_name() or p.usuario.email,
            p.get_estado_display(),
            precio,
            costo,
            total,
            iva,
            p.get_metodo_entrega_display(),
            p.get_metodo_pago_display(),
            p.creado.strftime("%d/%m/%Y %H:%M"),
            p.entregado_por or "-"
        ])


    for col_letter in ["D", "E", "F", "G"]:
        for cell in ws[col_letter][1:]:
            cell.number_format = '"$"#,##0'


    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                length = len(str(cell.value))
                if length > max_length:
                    max_length = length
            except:
                pass
        ws.column_dimensions[column].width = max_length + 3

    resumen = wb.create_sheet(title="Resumen")
    resumen_headers = ["Concepto", "Valor"]
    resumen.append(resumen_headers)

    resumen_datos = [
        ("Total Ventas (Precio)", total_precio),
        ("Total Costos", total_costo),
        ("Ganancia Total", total_ganancia),
        ("IVA Total (19%)", total_iva),
        ("Cantidad de Pedidos", len(pedidos)),
        ("Fecha de Generación", datetime.now().strftime("%d/%m/%Y %H:%M")),
    ]

    for item, valor in resumen_datos:
        resumen.append([item, valor])

    for cell in resumen["A"] + resumen["B"]:
        cell.border = Border(top=border_style, bottom=border_style, left=border_style, right=border_style)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for col in resumen.columns:
        col_letter = col[0].column_letter
        resumen.column_dimensions[col_letter].width = 25


    for col in resumen[1]:
        col.fill = header_fill
        col.font = header_font
        col.alignment = Alignment(horizontal="center")

    for cell in resumen["B"][1:5]:
        cell.number_format = '"$"#,##0'


    fecha_str = datetime.now().strftime("%d-%m-%Y")
    nombre_archivo = f"pedidos_financieros_{fecha_str}.xlsx"

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'

    wb.save(response)
    return response


from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import Pedido

@staff_member_required
def estadisticas_view(request):  
    pedidos = Pedido.objects.prefetch_related("items__producto")


    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    estado = request.GET.get("estado")

    if fecha_inicio:
        pedidos = pedidos.filter(creado__date__gte=fecha_inicio)
    if fecha_fin:
        pedidos = pedidos.filter(creado__date__lte=fecha_fin)
    if estado:
        pedidos = pedidos.filter(estado=estado)


    for p in pedidos:
        costo_total = Decimal(0)
        for i in p.items.all():
            precio_costo = i.producto.costo if i.producto.costo else Decimal(0)
            costo_total += precio_costo * Decimal(i.cantidad or 0)

        precio = Decimal(p.total or 0)
        ganancia = precio - costo_total
        iva = precio * Decimal("0.19")

        p.costo_total = round(costo_total, 2)
        p.ganancia = round(ganancia, 2)
        from math import ceil
        p.iva = Decimal(ceil(iva))

    total_ganancia = sum([p.ganancia for p in pedidos], Decimal(0))
    total_iva = sum([p.iva for p in pedidos], Decimal(0))
    cantidad_pedidos = pedidos.count()

    data_por_mes = (
        pedidos.values("creado__month")
        .annotate(
            ganancia_mes=Sum(
                ExpressionWrapper(F("total") - F("descuento") + F("envio"), output_field=DecimalField())
            )
        )
        .order_by("creado__month")
    )

    labels = [f"{m['creado__month']:02d}" for m in data_por_mes]
    values = [float(m["ganancia_mes"] or 0) for m in data_por_mes]
    mes_max = labels[values.index(max(values))] if values else "Sin datos"

    estados = Pedido.Estado.choices

    context = {
        "pedidos": pedidos,
        "labels": labels,
        "values": values,
        "total_ganancia": total_ganancia,
        "total_iva": total_iva,
        "cantidad_pedidos": cantidad_pedidos,
        "mes_max": mes_max,
        "estados": estados,
    }
    return render(request, "taller/estadisticas.html", context)

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CitaForm
from .models import Cita

def agendar_servicio(request):
    """Vista de agendamiento simple sin depender de profesionales."""
    if request.method == "POST":
        form = CitaForm(request.POST, user=request.user)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.usuario = request.user
            cita.save()
            messages.success(request, "✅ Tu cita fue agendada correctamente. Te contactaremos pronto.")
            return redirect("mis_citas")
    else:
        form = CitaForm(user=request.user)

    return render(request, "agendar.html", {"form": form})


from django.utils import timezone
from datetime import datetime, timedelta
from .models import BloqueHorario

def generar_bloques_si_faltan():
    """Crea bloques horarios futuros (09:00–18:00) para hoy y mañana si no existen."""
    if not BloqueHorario.objects.exists():
        hoy = timezone.localdate()
        for dia in [hoy, hoy + timedelta(days=1)]:
            for hora in range(9, 19):  # 9:00 a 18:00
                inicio_naive = datetime.combine(dia, datetime.min.time()) + timedelta(hours=hora)
                inicio = timezone.make_aware(inicio_naive, timezone.get_current_timezone())
                fin = inicio + timedelta(hours=1)
                BloqueHorario.objects.get_or_create(inicio=inicio, fin=fin, bloqueado=False)
        print("✅ Bloques horarios creados con zona horaria local.")

def agendar_servicio(request):
    """Vista para agendar citas."""
    from .forms import CitaForm
    from django.contrib import messages

    # 👇 Genera bloques si no hay ninguno
    generar_bloques_si_faltan()

    if request.method == "POST":
        form = CitaForm(request.POST, user=request.user)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.usuario = request.user
            cita.save()
            messages.success(request, "✅ Tu cita fue agendada correctamente. Te contactaremos pronto.")
            return redirect("mis_citas")
    else:
        form = CitaForm(user=request.user)

    return render(request, "agendar.html", {"form": form})

