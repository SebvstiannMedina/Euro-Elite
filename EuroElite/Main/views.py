from django.shortcuts import render

def home(request):
    return render(request, 'Taller/main.html')