# payments/views.py
import requests
from django.apps import apps
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

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

    # Asegurar Pago PENDIENTE
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

    body = {
        "apiKey": api_key,
        "commerceOrder": str(pedido.id),
        "subject": f"Pedido #{pedido.id}",
        "currency": "CLP",
        "amount": str(pedido.total),
        "email": getattr(pedido.usuario, "email", "") or "cliente@ejemplo.cl",
        "urlConfirmation": url_conf,
        "urlReturn": url_ret,
    }
    body["s"] = flow_sign(body, secret)

    # Llamada a Flow
    try:
        resp = requests.post(f"{api_base}/payment/create", data=body, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return HttpResponseBadRequest(f"Error de red al llamar a Flow: {e}")
    except ValueError:
        return HttpResponseBadRequest("Respuesta inválida de Flow (no JSON).")

    url = data.get("url")
    token = data.get("token")
    if not url or not token:
        return HttpResponseBadRequest(f"Respuesta inesperada de Flow: {data}")

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
    commerce_order = str(data.get("commerceOrder"))  # id del Pedido

    pedido = get_object_or_404(Pedido, id=commerce_order)
    pago = getattr(pedido, "pago", None)
    if not pago:
        pago = Pago.objects.create(
            pedido=pedido,
            metodo=Pedido.MetodoPago.PASARELA,
            monto=pedido.total,
            estado=Pago.Estado.PENDIENTE,
        )

    if status_flow == "1":
        pago.estado = Pago.Estado.COMPLETADO
        pedido.estado = Pedido.Estado.PAGADO
    elif status_flow == "3":
        pago.estado = Pago.Estado.FALLIDO

    pago.save()
    pedido.save()
    return JsonResponse({"ok": True})


def flow_retorno(request):
    """
    Endpoint donde el usuario vuelve desde Flow.
    """
    return JsonResponse({"mensaje": "Volviste desde Flow. Estamos procesando tu pago."})
