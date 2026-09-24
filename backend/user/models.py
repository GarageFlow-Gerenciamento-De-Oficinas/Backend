from __future__ import annotations
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> User:
        if not email:
            raise ValueError("Email inválido!")
        normalized_email = self.normalize_email(email)
        user = self.model(
            email = normalized_email,
            **extra_fields
        )
        if password is None:
            user.set_unusable_password()
        else:
            user.set_password(password)

        user.save(using=self._db)
        return user


    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any) -> User:
        if not password:
            raise ValueError("Superuser must have a password.")
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
    
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
    
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        user = self.create_user(email, password, **extra_fields)
        return user
    
class User(AbstractUser):
    username = None
    email = models.EmailField(
        verbose_name="E-mail",
        unique=True
    )
    address = models.CharField(verbose_name="Endereço", max_length=120)
    phone = models.CharField(verbose_name="Telefone para contato", max_length=11)
    created_at = models.DateTimeField(verbose_name="Data de criação", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Ultima atualização", auto_now=True)
    activated_at = models.DateTimeField(
        verbose_name="Data de ativação",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Usuário")
        verbose_name_plural = _("Usuários")


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects= UserManager()

class UserInvitation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invitations",)
    token_hash = models.CharField(max_length=64,)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,)