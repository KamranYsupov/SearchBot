from django.contrib import admin

from .models import Match

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    readonly_fields = (
        'message_link',
        'keyword',
        'created_at'
    )