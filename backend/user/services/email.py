from django.conf import settings
from django.core.mail import send_mail

from user.models import User

def send_invitation_email(
    user: User,
    token: str
) -> None:
    activation_url = (
        f"{settings.FRONTEND_URL}/activate?token={token}"
    )

    send_mail(
        subject="Convite para ativar sua conta - GarageFlow",
        message=(
            f"Olá, {user.first_name or 'usuário'}!\n\n"
            "Sua conta no GarageFlow foi criada.\n\n"
            "Acesse o link abaixo para definir sua senha e ativar sua conta:\n\n"
            f"{activation_url}\n\n"
            "Este convite é válido por 24 horas."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )