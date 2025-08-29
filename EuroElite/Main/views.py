from django.shortcuts import render

def home(request):
    return render(request, 'Taller/main.html')

def contacto(request):
    return render(request, 'Taller/contacto.html')

def equipo(request):
    return render(request, 'Taller/equipo.html')

def productos(request):
    return render(request, 'Taller/productos.html')

def inicio_crea_session(request):
    return render(request, 'Taller/inicio_crea_session.html')

