from django.test import TestCase

from user.models import User
from user.serializers.activation import UserActivationSerializer
from user.services.invitation import create_user_invitation


class UserActivationSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="joao@example.com",
            address="Rua das Flores, 123",
            phone="16999999999",
            password=None,
        )

        self.user.set_unusable_password()
        self.user.save(update_fields=["password"])

        self.invitation, self.token = create_user_invitation(
            self.user
        )

    def test_activate_user_with_valid_data(self):
        serializer = UserActivationSerializer(
            data={
                "token": self.token,
                "password": "MinhaSenha123!",
            }
        )

        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user, self.user)

        user.refresh_from_db()

        self.assertTrue(
            user.check_password("MinhaSenha123!")
        )

    def test_token_is_required(self):
        serializer = UserActivationSerializer(
            data={
                "password": "MinhaSenha123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("token", serializer.errors)

    def test_password_is_required(self):
        serializer = UserActivationSerializer(
            data={
                "token": self.token,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_password_must_have_minimum_length(self):
        serializer = UserActivationSerializer(
            data={
                "token": self.token,
                "password": "123",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_invalid_token_returns_validation_error(self):
        serializer = UserActivationSerializer(
            data={
                "token": "token-invalido",
                "password": "MinhaSenha123!",
            }
        )

        self.assertTrue(serializer.is_valid())

        with self.assertRaises(Exception):
            serializer.save()