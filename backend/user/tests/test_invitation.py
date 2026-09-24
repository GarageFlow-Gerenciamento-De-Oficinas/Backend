import hashlib

from django.test import TestCase
from django.utils import timezone

from user.models import User, UserInvitation
from user.services.invitation import (
    create_user_invitation,
    hash_invitation_token,
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