from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Расширенная модель пользователя"""
    phone_number = models.CharField('Телефон', max_length=20, blank=True, null=True)
    address = models.TextField('Адрес', blank=True, null=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True, null=True)
    inn = models.CharField('ИНН', max_length=12, blank=True, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """Профиль пользователя"""

    CURRENCY_CHOICES = [
        ('RUB', '₽ Рубль'),
        ('USD', '$ Доллар'),
        ('EUR', '€ Евро'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile',
        verbose_name='Пользователь'
    )
    monthly_budget = models.DecimalField(
        'Месячный бюджет',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    currency = models.CharField(
        'Валюта',
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='RUB'
    )
    notification_enabled = models.BooleanField(
        'Уведомления включены',
        default=True
    )
    email_notifications = models.BooleanField(
        'Email уведомления',
        default=False
    )
    ai_recommendations_enabled = models.BooleanField(
        'Рекомендации',
        default=True
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'