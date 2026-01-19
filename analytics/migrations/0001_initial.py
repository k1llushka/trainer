from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("transactions", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Budget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="Сумма бюджета"
                    ),
                ),
                ("period_start", models.DateField(verbose_name="Начало периода")),
                ("period_end", models.DateField(verbose_name="Конец периода")),
                (
                    "alert_threshold",
                    models.IntegerField(
                        default=80, verbose_name="Порог уведомления (%)"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analytics_budgets",
                        to="transactions.category",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analytics_budgets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Бюджет",
                "verbose_name_plural": "Бюджеты",
            },
        ),
        migrations.CreateModel(
            name="AIRecommendation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("saving", "Сбережения"),
                            ("investment", "Инвестиции"),
                            ("budget", "Бюджет"),
                            ("warning", "Предупреждение"),
                        ],
                        max_length=20,
                        verbose_name="Тип",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Заголовок")),
                ("description", models.TextField(verbose_name="Описание")),
                (
                    "data",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="Дополнительные данные"
                    ),
                ),
                (
                    "is_read",
                    models.BooleanField(default=False, verbose_name="Прочитано"),
                ),
                (
                    "is_applied",
                    models.BooleanField(default=False, verbose_name="Применено"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recommendations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "AI-рекомендация",
                "verbose_name_plural": "AI-рекомендации",
                "ordering": ["-created_at"],
            },
        ),
    ]