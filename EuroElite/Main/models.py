from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# ========== MODELO DE CITA ==========
class Cita(models.Model):
    SERVICIOS = [
        ('mantenimiento', 'Mantenimiento'),
        ('reparacion', 'Reparación'),
        ('diagnostico', 'Diagnóstico'),
        ('otros', 'Otros'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    servicio = models.CharField(max_length=50, choices=SERVICIOS)
    fecha = models.DateField()
    hora = models.TimeField()
    descripcion = models.TextField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.servicio} ({self.fecha} {self.hora})"
    
# ========== MODELO DE agregar rut y telefono ==========

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username