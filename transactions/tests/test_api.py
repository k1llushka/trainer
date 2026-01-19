from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class TransactionAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("user", password="12345")
        self.client.force_authenticate(self.user)

    def test_api_list_ok(self):
        url = reverse("api:transactions-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
