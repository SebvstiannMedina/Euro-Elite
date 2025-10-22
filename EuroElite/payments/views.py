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
    except Exception:
        pass

    return HttpResponseRedirect(f"{url}?token={token}")

@csrf_exempt
def flow_confirmacion(request):
    """
    Endpoint seguro para recibir notificaciones de Flow (server-to-server).
    """
    Pedido = apps.get_model('Main', 'Pedido')
    Pago   = apps.get_model('Main', 'Pago')

    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    token = _s(request.POST.get("token"))
    if not token:
        return HttpResponseBadRequest("Falta token")

    api_base = _s(settings.FLOW_API_BASE)
    api_key  = _s(settings.FLOW_API_KEY)
    secret   = _s(settings.FLOW_SECRET_KEY)

    params = {"apiKey": api_key, "token": token}
    params["s"] = flow_sign(params, secret)

    try:
        rs = requests.get(f"{api_base}/payment/getStatusExtended", params=params, timeout=20)
        rs.raise_for_status()
        data = rs.json()
    except requests.RequestException as e:
        return HttpResponseBadRequest(f"Error de red al consultar estado en Flow: {e}")
    except ValueError:
        return HttpResponseBadRequest("Respuesta inválida de Flow (no JSON).")

    status_flow = str(data.get("status"))            # 1=pagado, 2=pendiente, 3=fallido
    commerce_order = str(data.get("commerceOrder"))  # ej: "9-1700000000" o "9"

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
    if status_flow == "1":
        pago.estado = Pago.Estado.COMPLETADO
        pedido.estado = Pedido.Estado.PAGADO
        
        # ✅ DESCONTAR STOCK: solo cuando el pago es exitoso
        # Obtener el modelo Producto
        Producto = apps.get_model('Main', 'Producto')
        ItemPedido = apps.get_model('Main', 'ItemPedido')
        
        # Recorrer los items del pedido y descontar stock
        for item in pedido.items.select_related('producto'):
            producto = item.producto
            if producto and producto.stock is not None:
                # Descontar la cantidad solo si aún no se ha descontado
                # (en caso de múltiples notificaciones de Flow)
                nueva_stock = max(0, producto.stock - item.cantidad)
                if nueva_stock != producto.stock:
                    producto.stock = nueva_stock
                    producto.save(update_fields=['stock'])
        
    elif status_flow == "3":
        pago.estado = Pago.Estado.FALLIDO
    else:
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


def flow_retorno(request):
    """
    Endpoint donde el usuario vuelve desde Flow.
    Redirige a la página de compra exitosa.
    """
    # Flow envía el token como parámetro GET
    token = request.GET.get('token', '').strip()
    
    if not token:
        # Si no hay token, redirigir al home
        return redirect('home')
    
    # Intentar obtener el pedido asociado al token
    Pago = apps.get_model('Main', 'Pago')
    try:
        # Buscar el pago por token
        pago = Pago.objects.filter(flow_token=token).select_related('pedido').first()
        if pago and pago.pedido:
            # Redirigir a la página de éxito con el ID del pedido
            return redirect('compra_exitosa_detalle', pedido_id=pago.pedido.id)
    except Exception:
        pass
    
    # Fallback: redirigir a compra exitosa sin ID específico
    return redirect('compra_exitosa')
