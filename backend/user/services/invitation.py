import hashlib
import secrets
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from user.services.email import send_invitation_email
from user.models import UserInvitation, User

INVITATION_EXPIRATION_HOURS = 24

def generate_invitation_token() -> str:
    return secrets.token_urlsafe(32)

def hash_invitation_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

@transaction.atomic
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

@transaction.atomic
def resend_user_invitation(user: User) -> tuple[UserInvitation, str]:
    if user.activated_at is not None:
        raise ValueError("Este usuário já foi ativado.")

    now = timezone.now()

    UserInvitation.objects.filter(
        user=user,
        used_at__isnull=True,
        invalidated_at__isnull=True,
    ).update(
        invalidated_at=now,
    )

    invitation, token = create_user_invitation(user)

    send_invitation_email(user, token)

    return invitation, token

@transaction.atomic
def resend_user_invitation_by_email(email: str) -> tuple[UserInvitation, str]:
    user = User.objects.filter(email__iexact=email, is_active=True, activated_at__isnull=True).first()
    if user is None:
        return None

    return resend_user_invitation(user)