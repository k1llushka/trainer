from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """Инлайн для профиля пользователя"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ['monthly_budget', 'currency', 'notification_enabled', 'email_notifications', 'ai_recommendations_enabled']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для пользователя"""
    inlines = (UserProfileInline,)

    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone_number', 'address', 'avatar', 'passport_number', 'inn')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админка для профиля пользователя"""
    list_display = ['user', 'monthly_budget', 'currency', 'notification_enabled', 'created_at']
    list_filter = ['currency', 'notification_enabled', 'ai_recommendations_enabled']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Финансовые настройки', {
            'fields': ('monthly_budget', 'currency')
        }),
        ('Уведомления', {
            'fields': ('notification_enabled', 'email_notifications', 'ai_recommendations_enabled')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )