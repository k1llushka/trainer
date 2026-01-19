from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Card",
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
                    "card_number",
                    models.CharField(
                        max_length=19, unique=True, verbose_name="Номер карты"
                    ),
                ),
                (
                    "card_holder",
                    models.CharField(max_length=100, verbose_name="Держатель карты"),
                ),
                (
                    "card_type",
                    models.CharField(
                        choices=[("debit", "Дебетовая"), ("credit", "Кредитная")],
                        max_length=10,
                        verbose_name="Тип карты",
                    ),
                ),
                (
                    "card_system",
                    models.CharField(
                        choices=[
                            ("mir", "МИР"),
                            ("visa", "Visa"),
                            ("mastercard", "Mastercard"),
                        ],
                        default="mir",
                        max_length=20,
                        verbose_name="Платежная система",
                    ),
                ),
                (
                    "bank_name",
                    models.CharField(
                        default="VTB", max_length=100, verbose_name="Банк-эмитент"
                    ),
                ),
                (
                    "balance",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                        verbose_name="Баланс",
                    ),
                ),
                ("expiry_date", models.DateField(verbose_name="Срок действия")),
                ("cvv", models.CharField(blank=True, max_length=3, verbose_name="CVV")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Описание карты"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активна"),
                ),
                (
                    "color",
                    models.CharField(
                        default="#0066CC", max_length=7, verbose_name="Цвет карты"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cards",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Карта",
                "verbose_name_plural": "Карты",
            },
        ),
    ]