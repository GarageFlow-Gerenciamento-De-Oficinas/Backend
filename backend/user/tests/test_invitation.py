import hashlib

from django.core import mail
from django.urls import reverse

from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from user.models import User, UserInvitation
from user.services.invitation import (
    create_user_invitation,
    hash_invitation_token,
    resend_user_invitation,
)


class UserInvitationTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="joao@example.com",
            password="SenhaTemporaria123!",
            address="Rua das Flores, 123",
            phone="16999999999",
        )

    def test_create_user_invitation(self):
        invitation, token = create_user_invitation(self.user)
        self.assertIsInstance(invitation, UserInvitation)
        self.assertTrue(token)
        self.assertEqual(invitation.user, self.user)
        self.assertTrue(invitation.expires_at > timezone.now())

    def test_invitation_token_is_not_stored_directly(self):
        invitation, token = create_user_invitation(self.user)
        self.assertNotEqual(invitation.token_hash, token)
        self.assertEqual(invitation.token_hash, hash_invitation_token(token))

    def test_invitation_token_has_expected_hash(self):
        invitation, token = create_user_invitation(self.user)
        expected_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        self.assertEqual(invitation.token_hash, expected_hash)

    def test_resend_user_invitation(self):
        invitation, old_token = create_user_invitation(self.user)

        new_invitation, new_token = resend_user_invitation(self.user)

        invitation.refresh_from_db()

        self.assertIsNotNone(invitation.invalidated_at)
        self.assertNotEqual(old_token, new_token)

        self.assertEqual(
            new_invitation.user,
            self.user,
        )

        self.assertIsNone(new_invitation.used_at)
        self.assertIsNone(new_invitation.invalidated_at)

        self.assertEqual(
            new_invitation.token_hash,
            hash_invitation_token(new_token),
        )

    def test_resend_user_invitation_does_not_allow_activated_user(self):
        self.user.activated_at = timezone.now()
        self.user.save(update_fields=["activated_at"])

        with self.assertRaises(ValueError) as context:
            resend_user_invitation(self.user)

        self.assertEqual(
            str(context.exception),
            "Este usuário já foi ativado.",
        )

    def test_resend_user_invitation_sends_email(self):
        _, old_token = create_user_invitation(self.user)

        new_invitation, new_token = resend_user_invitation(self.user)

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(email.subject, "Convite para ativar sua conta - GarageFlow",)
        self.assertEqual(email.to, [self.user.email],)
        self.assertIn(new_token, email.body,)
        self.assertNotIn(old_token, email.body,)
        self.assertEqual(new_invitation.token_hash, hash_invitation_token(new_token),)

    def test_resend_invitation(self):
        user = User.objects.create_user(
            email="joao2@example.com",
            password=None,
            address="Rua das Flores, 123",
            phone="16999999999",
        )

        create_user_invitation(user)

        response = self.client.post(
            reverse("resend-invitation"),
            {"email": user.email,},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK,)

        self.assertEqual(
            response.data["detail"],
            (
                "Se o usuário estiver apto a receber um novo convite, "
                "um novo convite será enviado."
            ),
        )

        self.assertEqual(len(mail.outbox), 1)

    def test_resend_invitation_with_unknown_email(self):
        response = self.client.post(
            reverse("resend-invitation"),
            {
                "email": "naoexiste@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK,)

        self.assertEqual(
            response.data["detail"],
            (
                "Se o usuário estiver apto a receber um novo convite, "
                "um novo convite será enviado."
            ),
        )

        self.assertEqual(len(mail.outbox), 0)

    def test_resend_invitation_for_activated_user(self):
        user = User.objects.create_user(
            email="joao2@example.com",
            password="Senha123!",
            address="Rua das Flores, 123",
            phone="16999999999",
            activated_at=timezone.now(),
        )

        response = self.client.post(
            reverse("resend-invitation"),
            {
                "email": user.email,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK,)

        self.assertEqual(
            response.data["detail"],
            (
                "Se o usuário estiver apto a receber um novo convite, "
                "um novo convite será enviado."
            ),
        )

        self.assertEqual(len(mail.outbox), 0)

    def test_resend_invitation_with_invalid_email(self):
        response = self.client.post(
            reverse("resend-invitation"),
            {
                "email": "email-invalido",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("email", response.data)

        self.assertEqual(len(mail.outbox), 0)