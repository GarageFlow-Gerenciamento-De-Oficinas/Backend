from django.db import transaction
from django.utils import timezone

from user.models import UserInvitation, User
from .invitation import hash_invitation_token

class ActivationError(Exception):
    pass

@transaction.atomic
def activate_user(token: str, password: str) -> User:
    token_hash = hash_invitation_token(token)

    invitation = (
        UserInvitation.objects.select_related("user").filter(token_hash= token_hash).first()
    )

    if invitation is None:
        raise ActivationError("Convite inválido.")

    if invitation.used_at is not None:
        raise ActivationError("Este convite já foi utilizado.")

    if invitation.expires_at <= timezone.now():
        raise ActivationError("Este convite expirou.")

    user = invitation.user

    user.set_password(password)
    user.activated_at = timezone.now()
    user.save(update_fields=["password", "activated_at"])

    invitation.used_at = timezone.now()
    invitation.save(update_fields=["used_at"])

    return user