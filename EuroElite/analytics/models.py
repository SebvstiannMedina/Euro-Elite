from django.db import models

class Event(models.Model):
    ts = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(null=True, blank=True)
    session_id = models.CharField(max_length=64, null=True, blank=True)
    name = models.CharField(max_length=64)
    props = models.JSONField(default=dict)

    class Meta:
        indexes = [
            models.Index(fields=["name", "ts"]),
            models.Index(fields=["user_id", "ts"]), 
        ]

    def __str__(self):
        return f"{self.ts} - {self.name}"
