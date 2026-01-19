from django.test import TestCase
from django.contrib.auth import get_user_model
from transactions.models import Transaction, Category
from decimal import Decimal
from datetime import date

User = get_user_model()


class TransactionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            password="12345"
        )
        self.category = Category.objects.create(
            user=self.user,
            name="Еда",
            type="expense",
            color="#ff0000"
        )

    def test_create_transaction(self):
        """Проверяем, что транзакция создаётся корректно"""

        t = Transaction.objects.create(
            user=self.user,
            category=self.category,
            type="expense",
            amount=Decimal("250.50"),
            date=date.today(),
            description="Обед"
        )

        self.assertEqual(t.amount, Decimal("250.50"))
        self.assertEqual(t.type, "expense")
        self.assertEqual(str(t), f"{t.category} - {t.amount}")
