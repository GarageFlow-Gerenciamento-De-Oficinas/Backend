from django.urls import reverse

from rest_framework import status

from backend.tests.base import AuthenticatedAPITestCase
from user.models import User, UserInvitation


class UserAPITestCase(AuthenticatedAPITestCase):

    def test_create_user(self):
        data = {
            "email": "joao@example.com",
            "address": "Rua das Flores, 123",
            "phone": "16999999999",
        }

        url = reverse("user-list")

        response = self.client.post(url, data, format="json",)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED,)
        self.assertEqual(User.objects.count(), 2,)

        user = User.objects.get(email="joao@example.com")

        self.assertTrue(user.has_usable_password() is False)
        self.assertIsNone(user.activated_at)
        self.assertEqual(UserInvitation.objects.filter(user=user).count(), 1)
        self.assertTrue(response.data["invitation_token"])

    def test_create_user_does_not_accept_password(self):
        data = {
            "email": "maria@example.com",
            "address": "Rua Nova, 456",
            "phone": "16988888888",
            "password": "MinhaSenha123!",
        }
        url = reverse("user-list")
        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED,)

        user = User.objects.get(email="maria@example.com")

        self.assertFalse(user.has_usable_password())