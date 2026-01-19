from django.contrib import admin
from .models import Card

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'card_system',
        'card_type',
        'card_number_masked',
        'balance',
        'is_active',
        'created_at',
    )

    list_filter = ('card_type', 'card_system', 'is_active')
    search_fields = ('card_number', 'card_holder', 'user__username')
    readonly_fields = ('created_at',)
