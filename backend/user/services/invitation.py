import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone

from user.models import UserInvitation, User

INVITATION_EXPIRATION_HOURS = 24

def generate_invitation_token() -> str:
    return secrets.token_urlsafe(32)

def hash_invitation_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_user_invitation(user: User) -> tuple[UserInvitation, str]:
    token = generate_invitation_token()

    invitation = UserInvitation.objects.create(
        user=user,
        token_hash=hash_invitation_token(token),
        expires_at=(
            timezone.now() + timedelta(hours=INVITATION_EXPIRATION_HOURS)
        ),
    )

    return invitation, token