from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("ts", "name", "user_id", "session_id")
    list_filter = ("name",)
    search_fields = ("session_id", "user_id")
