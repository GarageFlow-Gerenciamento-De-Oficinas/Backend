from backend.tests.base import AuthenticatedAPITestCase
from rest_framework import status
from django.urls import reverse

from client.models import Client, Vehicle

class ClientAPITestCase(AuthenticatedAPITestCase):

    def setUp(self):
        super().setUp()
        self.client_data = {
            "name": "João da Silva",
            "email": "joao@example.com",
            "phone": "16999999999",
            "address": "Rua das Flores, 123",
        }

    def test_create_client(self):
        url = reverse("client-list")
        response = self.client.post(
            url,
            self.client_data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(response.data["name"], self.client_data["name"])

    def test_create_invalid_client(self):
        # Este teste deverá validar a constraint de contato
        data = self.client_data.copy()
        data["email"] = ""
        data["phone"] = ""
        url = reverse("client-list")
        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Client.objects.count(), 0)

    def test_create_same_client(self):
        Client.objects.create(**self.client_data)
        url = reverse("client-list")
        response = self.client.post(
            url,
            self.client_data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Client.objects.count(), 1)

    def test_list_clients(self):
        Client.objects.create(**self.client_data)
        url = reverse("client-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_deactivated_clients(self):
        Client.objects.create(**self.client_data, is_active=False)
        url = reverse("client-list")
        response = self.client.get(url, {"show": "not_active"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_all_clients(self):
        Client.objects.create(**self.client_data, is_active=False)
        new_client = {
            "name": "Julio da Silva",
            "email": "julio@example.com",
            "phone": "16999999999",
            "address": "Rua das Flores, 123",
        }
        Client.objects.create(**new_client, is_active=True)
        url = reverse("client-list")
        response = self.client.get(url, {"show": "all"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_client(self):
        client = Client.objects.create(**self.client_data)
        url = reverse("client-detail", kwargs={"pk": client.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], client.id)

    def test_get_invalid_client(self):
        url = reverse("client-detail", kwargs={"pk": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_client(self):
        client = Client.objects.create(**self.client_data)
        updated_data = {
            "name": "João Atualizado",
            "email": "joao.atualizado@example.com",
            "phone": "16888888888",
            "address": "Rua Nova, 456",
        }
        url = reverse("client-detail", kwargs={"pk": client.id})
        response = self.client.put(
            url,
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        client.refresh_from_db()
        self.assertEqual(client.name, updated_data["name"])
        self.assertEqual(client.email, updated_data["email"])

    def test_update_invalid_client(self):
        updated_data = {
            "name": "João Atualizado",
            "email": "joao.atualizado@example.com",
            "phone": "16888888888",
            "address": "Rua Nova, 456",
        }
        url = reverse("client-detail", kwargs={"pk": 1})
        response = self.client.put(
            url,
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_client_with_invalid_data(self):
        client = Client.objects.create(**self.client_data)
        updated_data = {
            "name": "João Atualizado",
            "email": "",
            "phone": "",
            "address": "Rua Nova, 456",
        }
        url = reverse("client-detail", kwargs={"pk": client.id})
        response = self.client.put(
            url,
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_client(self):
        client = Client.objects.create(**self.client_data)

        url = reverse(
            "client-detail",
            kwargs={"pk": client.id}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        client.refresh_from_db()
        self.assertEqual(
            Client.objects.filter(is_active=False).count(), 1
        )

    def test_get_client_vehicle(self):
        client = Client.objects.create(**self.client_data)
        vehicle = Vehicle.objects.create(
            client=client,
            plate="abc1234",
            brand="Toyota",
            model="i30",
            year=2020,
            color="branco"
        )
        url = reverse("client-vehicles", kwargs={"pk": client.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)