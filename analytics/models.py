from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Budget(models.Model):
    """Бюджеты по категориям"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics_budgets'
    )
    category = models.ForeignKey(
        'transactions.Category',
        on_delete=models.CASCADE,
        related_name='analytics_budgets'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    alert_threshold = models.IntegerField(default=80)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Бюджет {self.category.name}: {self.amount} руб."


class AIRecommendation(models.Model):
    """Рекомендации ИИ для пользователя"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_recommendations'
    )

    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AI рекомендация"
        verbose_name_plural = "AI рекомендации"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Рекомендация для {self.user} ({self.created_at:%Y-%m-%d})"
