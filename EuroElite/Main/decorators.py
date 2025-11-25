"""
Decoradores personalizados para control de acceso basado en roles.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """Requiere que el usuario sea administrador."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol != 'ADMIN':
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def mecanico_or_admin_required(view_func):
    """Requiere que el usuario sea mecánico o administrador."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in ['ADMIN', 'MECANICO']:
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def repartidor_or_admin_required(view_func):
    """Requiere que el usuario sea repartidor o administrador."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in ['ADMIN', 'REPARTIDOR']:
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def retiro_or_admin_required(view_func):
    """Requiere que el usuario sea encargado de retiro o administrador."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in ['ADMIN', 'RETIRO']:
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def despacho_or_admin_required(view_func):
    """Requiere que el usuario sea encargado de despacho o administrador."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in ['ADMIN', 'DESPACHO']:
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def asignador_or_admin_required(view_func):
    """Requiere que el usuario sea asignador de pedidos o administrador."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in ['ADMIN', 'ASIGNADOR']:
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper
