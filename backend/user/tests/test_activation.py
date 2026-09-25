from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from user.models import User, UserInvitation
from user.services.activation import ActivationError, activate_user
from user.services.invitation import create_user_invitation


class UserActivationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="joao@example.com",
            address="Rua das Flores, 123",
            phone="16999999999",
            password=None,
        )
        self.user.set_unusable_password()
        self.user.save(update_fields=["password"])

        self.invitation, self.token = create_user_invitation(self.user)

    def test_activate_user_with_valid_token(self):
        password = "MinhaSenhaSegura123!"

        user = activate_user(
            token=self.token,
            password=password,
        )

        user.refresh_from_db()
        self.invitation.refresh_from_db()

        self.assertEqual(user, self.user)
        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password(password))
        self.assertIsNotNone(user.activated_at)
        self.assertIsNotNone(self.invitation.used_at)

    def test_activate_user_with_invalid_token(self):
        with self.assertRaises(ActivationError) as context:
            activate_user(
                token="token-invalido",
                password="MinhaSenhaSegura123!",
            )

        self.assertEqual(
            str(context.exception),
            "Convite inválido.",
        )

        self.user.refresh_from_db()
        self.invitation.refresh_from_db()

        self.assertFalse(self.user.has_usable_password())
        self.assertIsNone(self.user.activated_at)
        self.assertIsNone(self.invitation.used_at)

    def test_activate_user_with_expired_invitation(self):
        self.invitation.expires_at = (
            timezone.now() - timedelta(minutes=1)
        )
        self.invitation.save(update_fields=["expires_at"])

        with self.assertRaises(ActivationError) as context:
            activate_user(
                token=self.token,
                password="MinhaSenhaSegura123!",
            )

        self.assertEqual(
            str(context.exception),
            "Este convite expirou.",
        )

        self.user.refresh_from_db()

        self.assertFalse(self.user.has_usable_password())
        self.assertIsNone(self.user.activated_at)

    def test_activate_user_with_used_invitation(self):
        self.invitation.used_at = timezone.now()
        self.invitation.save(update_fields=["used_at"])

        with self.assertRaises(ActivationError) as context:
            activate_user(
                token=self.token,
                password="MinhaSenhaSegura123!",
            )

        self.assertEqual(
            str(context.exception),
            "Este convite já foi utilizado.",
        )

        self.user.refresh_from_db()

        self.assertFalse(self.user.has_usable_password())
        self.assertIsNone(self.user.activated_at)

    def test_activate_user_with_invalidated_invitation(self):
        invitation, token = create_user_invitation(self.user)

        invitation.invalidated_at = timezone.now()

        
        invitation.save(update_fields=["invalidated_at"])

        with self.assertRaises(ActivationError) as context:
            activate_user(
                token=token,
                password="NovaSenha123!",
            )

        self.assertEqual(
            str(context.exception),
            "Este convite foi invalidado.",
        )

    def test_activation_token_can_only_be_used_once(self):
        password = "MinhaSenhaSegura123!"

        activate_user(
            token=self.token,
            password=password,
        )

        with self.assertRaises(ActivationError) as context:
            activate_user(
                token=self.token,
                password="OutraSenha123!",
            )

        self.assertEqual(
            str(context.exception),
            "Este convite já foi utilizado.",
        )

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password(password))
        self.assertFalse(self.user.check_password("OutraSenha123!"))