from django.db import models
from django.conf import settings

class Card(models.Model):
    """Банковские карты"""

    CARD_TYPES = [
        ('debit', 'Дебетовая'),
        ('credit', 'Кредитная'),
    ]

    CARD_SYSTEMS = [
        ('mir', 'МИР'),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    card_number = models.CharField(
        max_length=19,
        unique=True,
        verbose_name='Номер карты'
    )

    card_holder = models.CharField(
        max_length=100,
        verbose_name='Держатель карты'
    )

    card_type = models.CharField(
        max_length=10,
        choices=CARD_TYPES,
        verbose_name='Тип карты'
    )

    card_system = models.CharField(
        max_length=20,
        choices=CARD_SYSTEMS,
        default='mir',
        verbose_name='Платежная система'
    )

    bank_name = models.CharField(
        max_length=100,
        default='VTB',
        verbose_name='Банк-эмитент'
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Баланс'
    )

    expiry_date = models.DateField(verbose_name='Срок действия')
    cvv = models.CharField(max_length=3, verbose_name='CVV', blank=True)

    description = models.TextField(
        blank=True,
        verbose_name='Описание карты'
    )

    is_active = models.BooleanField(default=True, verbose_name='Активна')

    color = models.CharField(
        max_length=7,
        default='#0066CC',
        verbose_name='Цвет карты'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Карта'
        verbose_name_plural = 'Карты'

    def _last_digits(self) -> str:
        """Возвращает последние 4 цифры номера карты без пробелов и дефисов."""
        digits = ''.join(ch for ch in self.card_number if ch.isdigit())
        return digits[-4:] if len(digits) >= 4 else digits or self.card_number

    def __str__(self):
        return f"{self.card_system.upper()} **** {self._last_digits()}"

    @property
    def card_number_masked(self):
        """Маскированный номер карты"""
        return f"**** **** **** {self._last_digits()}"