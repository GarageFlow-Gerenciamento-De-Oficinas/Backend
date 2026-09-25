from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import User, UserInvitation
from user.services.invitation import create_user_invitation


class UserActivationAPITestCase(APITestCase):

    def test_activate_user(self):
        user = User.objects.create_user(
            email="joao@example.com",
            password=None,
            address="Rua das Flores, 123",
            phone="16999999999",
        )

        _, token = create_user_invitation(user)

        response = self.client.post(
            reverse("activate"),
            {
                "token": token,
                "password": "NovaSenha123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK,)

        user.refresh_from_db()

        self.assertTrue(user.has_usable_password())
        self.assertIsNotNone(user.activated_at)

        invitation = UserInvitation.objects.get(user=user)

        self.assertIsNotNone(invitation.used_at)

        self.assertTrue(user.check_password("NovaSenha123!"))

        self.assertEqual(response.data["detail"], "Usuário ativado com sucesso.",)

    def test_activate_user_with_invalid_token(self):
        response = self.client.post(
            reverse("activate"),
            {
                "token": "token-invalido",
                "password": "NovaSenha123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["token"],
            "Convite inválido.",
        )

    def test_activate_user_with_expired_invitation(self):
        user = User.objects.create_user(
            email="joao@example.com",
            password=None,
            address="Rua das Flores, 123",
            phone="16999999999",
        )

        invitation, token = create_user_invitation(user)

        invitation.expires_at = timezone.now() - timedelta(minutes=1)
        invitation.save(update_fields=["expires_at"])

        response = self.client.post(
            reverse("activate"),
            {
                "token": token,
                "password": "NovaSenha123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data["token"],
            "Este convite expirou.",
        )

    def test_activate_user_with_used_invitation(self):
        user = User.objects.create_user(
            email="joao@example.com",
            password=None,
            address="Rua das Flores, 123",
            phone="16999999999",
        )

        _, token = create_user_invitation(user)

        first_response = self.client.post(
            reverse("activate"),
            {
                "token": token,
                "password": "NovaSenha123!",
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        second_response = self.client.post(
            reverse("activate"),
            {
                "token": token,
                "password": "OutraSenha123!",
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            second_response.data["token"],
            "Este convite já foi utilizado.",
        )

    def test_activate_user_with_short_password(self):
        user = User.objects.create_user(
            email="joao@example.com",
            password=None,
            address="Rua das Flores, 123",
            phone="16999999999",
        )

        _, token = create_user_invitation(user)

        response = self.client.post(
            reverse("activate"),
            {
                "token": token,
                "password": "1234567",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "Ensure this field has at least 8 characters.",
            response.data["password"],
        )

    def test_activated_user_can_login(self):
        user = User.objects.create_user(
            email="joao@example.com",
            password=None,
            address="Rua das Flores, 123",
            phone="16999999999",
        )

        _, token = create_user_invitation(user)

        activation_response = self.client.post(
            reverse("activate"),
            {
                "token": token,
                "password": "NovaSenha123!",
            },
            format="json",
        )

        self.assertEqual(
            activation_response.status_code,
            status.HTTP_200_OK,
        )

        login_response = self.client.post(
            reverse("login"),
            {
                "email": "joao@example.com",
                "password": "NovaSenha123!",
            },
            format="json",
        )

        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)