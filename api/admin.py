from django.contrib import admin
from .models import Transcript


class TranscriptAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "timestamp")
    search_fields = ("user", "message")
admin.site.register(Transcript)
