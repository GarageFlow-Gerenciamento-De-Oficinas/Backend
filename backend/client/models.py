from django.db import models
from django.utils.translation import gettext_lazy as _

class Client(models.Model):
    name = models.CharField(verbose_name="Nome do cliente", max_length=60)
    email = models.EmailField(verbose_name="Email para contato", blank = True)
    phone = models.CharField(verbose_name="Telefone para contato", max_length=11, blank=True)
    address = models.CharField(verbose_name="Endereço", blank=True)
    active = models.BooleanField(verbose_name="Ativo", default=True)
    created_at = models.DateTimeField(verbose_name="Data de criação", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Ultima atualização", auto_now=True)

    class Meta:
        verbose_name = _("Cliente")
        verbose_name_plural = _("Clientes")

        constraints = [
            # Essa constraint é necessária pois o cliente precisa ter pelo menos um meio de contato
            models.CheckConstraint(
                condition=(
                    models.Q(email__gt="") | models.Q(phone__gt="")
                ),
                name="client_has_contact"
            ),
            models.UniqueConstraint(
                fields= ["name"],
                name = "unique_client_constraint"
            )
        ]

class Vehicle(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="vehicles",)
    plate = models.CharField(verbose_name="Placa do veiculo", max_length=7)
    brand = models.CharField(verbose_name="Marca do veiculo", max_length=60)
    model = models.CharField(verbose_name="Modelo do veiculo", max_length=60)
    year = models.CharField(verbose_name="Ano do veiculo", max_length=4)
    color = models.CharField(verbose_name="Cor do veiculo", max_length=30)
    active = models.BooleanField(verbose_name="Veiculo ativo", default=True)
    created_at = models.DateTimeField(verbose_name="Data de criação", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Ultima atualização", auto_now=True)

    class Meta:
        verbose_name = _("Veiculo")
        verbose_name_plural = _("Veiculos")

        constraints = [
            models.UniqueConstraint(
                fields= ["plate"],
                condition=models.Q(active=True),
                name = "unique_car_constraint"
            )
        ]