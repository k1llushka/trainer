from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from transactions.models import Transaction, Category
from decimal import Decimal
from datetime import date

User = get_user_model()


class TransactionListViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            password="12345"
        )
        self.client.login(username="tester", password="12345")

        category = Category.objects.create(
            user=self.user,
            name="Продукты",
            type="expense",
            color="#00ff00"
        )

        Transaction.objects.create(
            user=self.user,
            category=category,
            type="expense",
            amount=Decimal("300.00"),
            date=date.today()
        )

    def test_list_view_status(self):
        url = reverse("transactions:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_view_contains_transaction(self):
        url = reverse("transactions:list")
        response = self.client.get(url)
        self.assertContains(response, "300")

