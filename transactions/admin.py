from django.contrib import admin
from .models import Category, Transaction, Budget


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'icon', 'color', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'user']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'amount', 'category', 'date', 'created_at']
    list_filter = ['type', 'category', 'date', 'user']
    search_fields = ['description']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'month', 'created_at']
    list_filter = ['user', 'category', 'month']
    ordering = ['-month']