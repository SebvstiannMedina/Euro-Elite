import requests
from django.apps import apps
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .utils import flow_sign


def _s(x):
    """strip seguro para strings; devuelve '' si viene None."""
    return (x or "").strip()


@csrf_exempt
def flow_crear_orden(request):
    Pedido = apps.get_model('Main', 'Pedido')
    Pago   = apps.get_model('Main', 'Pago')

    try:
        print("FLOW crear | GET:", dict(request.GET), "| POST:", dict(request.POST))
    except Exception:
        pass

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

    # Credenciales/URLs saneadas
    api_base = _s(settings.FLOW_API_BASE)
    api_key  = _s(settings.FLOW_API_KEY)
    secret   = _s(settings.FLOW_SECRET_KEY)
    url_conf = _s(settings.FLOW_URL_CONFIRMATION)
    url_ret  = _s(settings.FLOW_URL_RETURN)   

    # Parametros para crear orden
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

    try:
        print("FLOW crear | BASE:", api_base, "| apiKey.len:", len(api_key), "| secret.len:", len(secret))
        print("FLOW crear | urlConfirmation:", url_conf, "| urlReturn:", url_ret)
    except Exception:
        pass

    # Llamada a Flow
    try:
        resp = requests.post(f"{api_base}/payment/create", data=body, timeout=20)
    except requests.RequestException as e:
        print("FLOW crear | network error:", repr(e))
        return HttpResponseBadRequest(f"Error de red al llamar a Flow: {e}")

    try:
        print("FLOW crear | status:", resp.status_code, "| text:", resp.text)
    except Exception:
        pass

    if resp.status_code != 200:
        return HttpResponseBadRequest(f"Error Flow: {resp.text}")

    try:
        data = resp.json()
    except ValueError:
        return HttpResponseBadRequest("Respuesta inválida de Flow (no JSON).")

    url = data.get("url")
    token = data.get("token")
    if not url or not token:
        return HttpResponseBadRequest(f"Respuesta inesperada de Flow: {data}")

    return HttpResponseRedirect(f"{url}?token={token}")


@csrf_exempt
def flow_confirmacion(request):
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
    except requests.RequestException as e:
        print("FLOW confirm | network error:", repr(e))
        return HttpResponseBadRequest(f"Error de red al consultar estado en Flow: {e}")

    try:
        print("FLOW confirm | status:", rs.status_code, "| text:", rs.text)
    except Exception:
        pass

    if rs.status_code != 200:
        return HttpResponseBadRequest(f"Error Flow al consultar estado: {rs.text}")

    try:
        data = rs.json()
    except ValueError:
        return HttpResponseBadRequest("Respuesta inválida de Flow (no JSON).")

    status_flow = str(data.get("status"))            # 1=pagado, 2=pendiente, 3=fallido
    commerce_order = str(data.get("commerceOrder"))  # = Pedido.id

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
    # "2" = pendiente → no cambiamos pedido a pagado

    pago.save()
    pedido.save()
    return JsonResponse({"ok": True})


def flow_retorno(request):
    return JsonResponse({"mensaje": "Volviste desde Flow. Estamos procesando tu pago."})