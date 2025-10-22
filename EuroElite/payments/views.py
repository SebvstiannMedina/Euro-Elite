# payments/views.py
import requests
from django.apps import apps
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect
import time
import uuid


from .utils import flow_sign

def _s(x):
    """strip seguro para strings; devuelve '' si viene None."""
    return (x or "").strip()


@csrf_exempt
def flow_crear_orden(request):
    """
    Crea la orden en Flow y redirige al usuario a la pasarela de pagos.
    Exento de CSRF porque es solo redirección POST desde nuestro frontend.
    """
    Pedido = apps.get_model('Main', 'Pedido')
    Pago   = apps.get_model('Main', 'Pago')

    pedido_id = (
        request.GET.get("pedido_id")
        or request.POST.get("pedido_id")
        or (getattr(request, "resolver_match", None) and request.resolver_match.kwargs.get("pedido_id"))
    )
    if not pedido_id:
        return HttpResponseBadRequest("Falta pedido_id")

    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Asegurar Pago PENDIENTE (crea uno si no existe)
    pago = getattr(pedido, "pago", None)
    if not pago:
        pago = Pago.objects.create(
            pedido=pedido,
            metodo=Pedido.MetodoPago.PASARELA,
            monto=pedido.total,
            estado=Pago.Estado.PENDIENTE,
        )

    # Credenciales y URLs
    api_base = _s(settings.FLOW_API_BASE)
    api_key  = _s(settings.FLOW_API_KEY)
    secret   = _s(settings.FLOW_SECRET_KEY)
    url_conf = _s(settings.FLOW_URL_CONFIRMATION)
    url_ret  = _s(settings.FLOW_URL_RETURN)

    # Validaciones básicas
    if not api_base or not api_key or not secret:
        return HttpResponseBadRequest("Configuración Flow incompleta (FLOW_API_BASE / FLOW_API_KEY / FLOW_SECRET_KEY).")
    if not (url_conf.startswith("http://") or url_conf.startswith("https://")):
        return HttpResponseBadRequest("FLOW_URL_CONFIRMATION debe ser una URL completa con http(s).")
    if not (url_ret.startswith("http://") or url_ret.startswith("https://")):
        return HttpResponseBadRequest("FLOW_URL_RETURN debe ser una URL completa con http(s).")

    # Asegurar amount entero (CLP)
    try:
        amount_int = int(round(float(pedido.total)))
    except Exception:
        return HttpResponseBadRequest("Monto inválido para Flow (debe ser número entero en CLP).")

    # Generar commerceOrder único: "<pedido_id>-<timestamp>"
    commerce_order = f"{pedido.id}-{int(time.time())}"

    body = {
        "apiKey": api_key,
        "commerceOrder": commerce_order,
        "subject": f"Pedido #{pedido.id} - Intento {commerce_order}",
        "currency": "CLP",
        "amount": str(amount_int),
        "email": getattr(pedido.usuario, "email", "") or "cliente@ejemplo.cl",
        "urlConfirmation": url_conf,
        "urlReturn": url_ret,
    }
    body["s"] = flow_sign(body, secret)

    # Intentar guardar commerce_order en Pago para trazabilidad si existe el campo
    try:
        if hasattr(pago, "commerce_order"):
            pago.commerce_order = commerce_order
            pago.save()
    except Exception:
        # no crítico si el campo no existe o hay error
        pass

    # Llamada a Flow (mejor manejo de errores y logging para depuración)
    try:
        print("FLOW -> POST:", f"{api_base}/payment/create")
        print("FLOW -> BODY:", body)
        print("FLOW -> s:", body.get("s"))

        resp = requests.post(f"{api_base}/payment/create", data=body, timeout=20)

        # Si no es 2xx, mostramos el body de respuesta para entender el 400
        if resp.status_code != 200:
            texto = resp.text
            try:
                texto_json = resp.json()
            except ValueError:
                texto_json = None
            return HttpResponseBadRequest(
                f"Flow devolvió status {resp.status_code}. Texto: {texto}. JSON: {texto_json}"
            )

        data = resp.json()

    except requests.RequestException as e:
        resp_text = getattr(e, "response", None) and getattr(e.response, "text", None)
        return HttpResponseBadRequest(f"Error de red al llamar a Flow: {e}. Resp: {resp_text}")
    except ValueError:
        return HttpResponseBadRequest("Respuesta inválida de Flow (no JSON).")

    url = data.get("url")
    token = data.get("token")
    if not url or not token:
        return HttpResponseBadRequest(f"Respuesta inesperada de Flow: {data}")

    # Guardar token en Pago para poder relacionar confirmaciones
    try:
        if hasattr(pago, "flow_token"):
            pago.flow_token = token
            pago.save()
            print(f"[FLOW_CREAR_ORDEN] Token guardado en Pago: {token} para pedido {pedido.id}")
    except Exception as e:
        print(f"[FLOW_CREAR_ORDEN] Error guardando token: {e}")

    url_retorno_con_id = f"{url_ret}?pedido_id={pedido.id}"
    
    print(f"[FLOW_CREAR_ORDEN] Redirigiendo a Flow con token: {token}")
    print(f"[FLOW_CREAR_ORDEN] URL de retorno configurada: {url_retorno_con_id}")
    
    return HttpResponseRedirect(f"{url}?token={token}")

@csrf_exempt
def flow_confirmacion(request):
    """
    Endpoint seguro para recibir notificaciones de Flow (server-to-server).
    """
    print(f"[FLOW_CONFIRMACION] ========== WEBHOOK RECIBIDO ==========")
    print(f"[FLOW_CONFIRMACION] Método: {request.method}")
    print(f"[FLOW_CONFIRMACION] POST data: {dict(request.POST)}")
    
    Pedido = apps.get_model('Main', 'Pedido')
    Pago   = apps.get_model('Main', 'Pago')

    if request.method != "POST":
        print(f"[FLOW_CONFIRMACION] ❌ Método no permitido: {request.method}")
        return HttpResponseBadRequest("Método no permitido")

    token = _s(request.POST.get("token"))
    if not token:
        print(f"[FLOW_CONFIRMACION] ❌ Falta token")
        return HttpResponseBadRequest("Falta token")
    
    print(f"[FLOW_CONFIRMACION] Token recibido: {token}")

    api_base = _s(settings.FLOW_API_BASE)
    api_key  = _s(settings.FLOW_API_KEY)
    secret   = _s(settings.FLOW_SECRET_KEY)

    params = {"apiKey": api_key, "token": token}
    params["s"] = flow_sign(params, secret)

    try:
        print(f"[FLOW_CONFIRMACION] Consultando estado en Flow...")
        rs = requests.get(f"{api_base}/payment/getStatusExtended", params=params, timeout=20)
        rs.raise_for_status()
        data = rs.json()
        print(f"[FLOW_CONFIRMACION] Respuesta de Flow: {data}")
    except requests.RequestException as e:
        print(f"[FLOW_CONFIRMACION] ❌ Error de red: {e}")
        return HttpResponseBadRequest(f"Error de red al consultar estado en Flow: {e}")
    except ValueError:
        print(f"[FLOW_CONFIRMACION] ❌ Respuesta inválida (no JSON)")
        return HttpResponseBadRequest("Respuesta inválida de Flow (no JSON).")

    status_flow = str(data.get("status"))            # 1=pagado, 2=pendiente, 3=fallido
    commerce_order = str(data.get("commerceOrder"))  # ej: "9-1700000000" o "9"
    
    print(f"[FLOW_CONFIRMACION] status_flow: {status_flow}")
    print(f"[FLOW_CONFIRMACION] commerce_order: {commerce_order}")

    # Extraer pedido_id desde commerceOrder (antes del primer '-')
    if "-" in commerce_order:
        pedido_id = commerce_order.split("-", 1)[0]
    else:
        pedido_id = commerce_order

    # Obtener Pedido
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Intentar encontrar el Pago asociado:
    pago = None
    token_from_flow = _s(request.POST.get("token")) or _s(data.get("token") or "")
    if token_from_flow:
        try:
            pago = Pago.objects.filter(pedido=pedido, flow_token=token_from_flow).first()
        except Exception:
            pago = None

    if not pago:
        try:
            pago = Pago.objects.filter(pedido=pedido, commerce_order=commerce_order).first()
        except Exception:
            pago = None

    if not pago:
        pago = Pago.objects.filter(pedido=pedido).order_by("-id").first()

    if not pago:
        pago = Pago.objects.create(
            pedido=pedido,
            metodo=Pedido.MetodoPago.PASARELA,
            monto=pedido.total,
            estado=Pago.Estado.PENDIENTE,
        )

    # Actualizar estados según status_flow
    # IMPORTANTE: En Flow Sandbox, los pagos pueden quedar con status = 2 (PENDIENTE)
    # pero en realidad están aprobados. Verificar paymentData para confirmar.
    payment_data = data.get('paymentData', {})
    has_payment_data = payment_data and payment_data.get('authorizationCode')
    
    # Considerar exitoso si:
    # - status = 1 (pagado definitivo), O
    # - status = 2 (pendiente) PERO tiene paymentData con código de autorización (pago aprobado en sandbox)
    is_paid = status_flow == "1" or (status_flow == "2" and has_payment_data)
    
    if is_paid:
        print(f"[FLOW_CONFIRMACION] ✅ Pago EXITOSO - status_flow = {status_flow}, tiene authCode = {has_payment_data}")
        pago.estado = Pago.Estado.COMPLETADO
        pedido.estado = Pedido.Estado.PAGADO
        
        # ✅ DESCONTAR STOCK: solo cuando el pago es exitoso
        # Obtener el modelo Producto
        Producto = apps.get_model('Main', 'Producto')
        ItemPedido = apps.get_model('Main', 'ItemPedido')
        
        print(f"[FLOW_CONFIRMACION] Descontando stock para pedido {pedido.id}")
        
        # Recorrer los items del pedido y descontar stock
        for item in pedido.items.select_related('producto'):
            producto = item.producto
            if producto and producto.stock is not None:
                stock_antes = producto.stock
                # Descontar la cantidad solo si aún no se ha descontado
                # (en caso de múltiples notificaciones de Flow)
                nueva_stock = max(0, producto.stock - item.cantidad)
                if nueva_stock != producto.stock:
                    producto.stock = nueva_stock
                    producto.save(update_fields=['stock'])
                    print(f"[FLOW_CONFIRMACION] Producto '{producto.nombre}': stock {stock_antes} → {nueva_stock} (descontado {item.cantidad})")
                else:
                    print(f"[FLOW_CONFIRMACION] Producto '{producto.nombre}': stock ya está en {producto.stock} (no se descuenta)")
            else:
                print(f"[FLOW_CONFIRMACION] Item {item.id}: producto={producto}, stock={'None' if not producto else producto.stock}")
        
    elif status_flow == "3":
        print(f"[FLOW_CONFIRMACION] ❌ Pago FALLIDO - status_flow = 3")
        pago.estado = Pago.Estado.FALLIDO
        pedido.estado = Pedido.Estado.CANCELADO
        
        # Opcional: Registrar el motivo del rechazo si Flow lo proporciona
        last_error = data.get('lastError', {})
        if last_error and last_error.get('message'):
            print(f"[FLOW_CONFIRMACION] Motivo del rechazo: {last_error.get('message')}")
        
    else:
        print(f"[FLOW_CONFIRMACION] ⏳ Pago PENDIENTE - status_flow = {status_flow}, sin paymentData")
        pago.estado = Pago.Estado.PENDIENTE

    # Guardar respuesta cruda y token en Pago si existen los campos
    try:
        if hasattr(pago, "flow_response"):
            pago.flow_response = str(data)
        if token_from_flow and hasattr(pago, "flow_token"):
            pago.flow_token = token_from_flow
    except Exception:
        pass

    pago.save()
    pedido.save()
    return JsonResponse({"ok": True})


@csrf_exempt
def flow_retorno(request):
    """
    Endpoint donde el usuario vuelve desde Flow.
    Redirige a la página de compra exitosa.
    """
    # Flow envía el token como parámetro GET
    token = request.GET.get('token', '').strip()
    pedido_id_url = request.GET.get('pedido_id', '').strip()  # Por si lo enviamos nosotros
    
    print(f"[FLOW_RETORNO] ========== INICIO ==========")
    print(f"[FLOW_RETORNO] Token recibido: '{token}'")
    print(f"[FLOW_RETORNO] Pedido ID en URL: '{pedido_id_url}'")
    print(f"[FLOW_RETORNO] Usuario autenticado: {request.user.is_authenticated}")
    print(f"[FLOW_RETORNO] Session ID: {request.session.session_key}")
    print(f"[FLOW_RETORNO] Session keys: {list(request.session.keys())}")
    print(f"[FLOW_RETORNO] Todos los GET params: {dict(request.GET)}")
    
    pedido_id_sesion = request.session.get('last_order_id')
    print(f"[FLOW_RETORNO] Pedido ID desde sesión: {pedido_id_sesion}")
    
    # Intentar obtener el pedido asociado al token
    Pago = apps.get_model('Main', 'Pago')
    Pedido = apps.get_model('Main', 'Pedido')
    
    pedido_id = None
    
    # Buscar por token de Flow (si existe)
    if token:
        try:
            pago = Pago.objects.filter(flow_token=token).select_related('pedido').first()
            print(f"[FLOW_RETORNO] Pago encontrado por token: {pago}")
            
            if pago and pago.pedido:
                pedido_id = pago.pedido.id
                print(f"[FLOW_RETORNO] ✅ Pedido ID desde pago por token: {pedido_id}")
        except Exception as e:
            print(f"[FLOW_RETORNO] Error al buscar pago por token: {e}")
    else:
        print(f"[FLOW_RETORNO] ⚠️ No hay token de Flow")
    
    # Usar pedido_id de URL 
    if not pedido_id and pedido_id_url:
        try:
            pedido_id = int(pedido_id_url)
            print(f"[FLOW_RETORNO] ✅ Usando pedido_id de URL: {pedido_id}")
        except (ValueError, TypeError):
            print(f"[FLOW_RETORNO] ❌ pedido_id de URL inválido: {pedido_id_url}")
    
    # Usar pedido_id de sesión
    if not pedido_id and pedido_id_sesion:
        pedido_id = pedido_id_sesion
        print(f"[FLOW_RETORNO] ✅ Usando pedido_id de sesión: {pedido_id}")

    # Si el usuario está autenticado, buscar su último pedido
    if not pedido_id and request.user.is_authenticated:
        try:
            ultimo_pedido = Pedido.objects.filter(usuario=request.user).order_by('-creado').first()
            if ultimo_pedido:
                pedido_id = ultimo_pedido.id
                print(f"[FLOW_RETORNO] ✅ Usando último pedido del usuario: {pedido_id}")
        except Exception as e:
            print(f"[FLOW_RETORNO] Error buscando último pedido: {e}")
    
    if pedido_id:
        # Verificar el estado del pedido antes de redirigir
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            print(f"[FLOW_RETORNO] Estado del pedido: {pedido.estado}")
            
            # Si el pedido fue cancelado (pago rechazado), redirigir a página de rechazo
            if pedido.estado == Pedido.Estado.CANCELADO:
                print(f"[FLOW_RETORNO] 🚫 Pedido CANCELADO - redirigiendo a compra_rechazada")
                print(f"[FLOW_RETORNO] ========== FIN ==========")
                return redirect('compra_rechazada', pedido_id=pedido_id)
        except Pedido.DoesNotExist:
            print(f"[FLOW_RETORNO] ⚠️ Pedido {pedido_id} no existe")
        
        print(f"[FLOW_RETORNO] 🎯 Redirigiendo a compra_exitosa_detalle con pedido_id={pedido_id}")
        print(f"[FLOW_RETORNO] ========== FIN ==========")
        return redirect('compra_exitosa_detalle', pedido_id=pedido_id)
    
    print("[FLOW_RETORNO] ❌ No se pudo determinar pedido_id")
    print("[FLOW_RETORNO] Redirigiendo a compra_exitosa genérica")
    print(f"[FLOW_RETORNO] ========== FIN ==========")
    return redirect('compra_exitosa')
