from django.urls import path
from . import views

urlpatterns = [
    path("track/", views.track_event, name="analytics_track"),
    path("health/", views.health, name="analytics_health"),
]
