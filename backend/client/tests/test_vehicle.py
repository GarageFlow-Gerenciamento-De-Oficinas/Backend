from backend.tests.base import AuthenticatedAPITestCase
from rest_framework import status
from django.urls import reverse

from client.models import Client, Vehicle

class VehicleAPITestCase(AuthenticatedAPITestCase):

    def setUp(self):
        super().setUp()
        client_data = {
            "name": "João da Silva",
            "email": "joao@example.com",
            "phone": "16999999999",
            "address": "Rua das Flores, 123",
        }
        self.client_info = Client.objects.create(**client_data)
        self.vehicle_data = {
            "client": self.client_info,
            "plate": "ABC1234",
            "brand": "Toyota",
            "model": "i30",
            "year": "2020",
            "color": "branco",
        }

        self.vehicle_payload = {
            "client": self.client_info.id,
            "plate": "ABC1234",
            "brand": "Toyota",
            "model": "i30",
            "year": "2020",
            "color": "branco",
        }

    def test_create_vehicle(self):
        url = reverse("vehicle-list")
        response = self.client.post(
            url,
            self.vehicle_payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehicle.objects.count(), 1)
        self.assertEqual(response.data["plate"], self.vehicle_data["plate"])

    def test_update_nonexistent_vehicle(self):
        data = self.vehicle_payload.copy()
        data["plate"] = ""
        data["brand"] = ""
        url = reverse("vehicle-list")
        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vehicle.objects.count(), 0)

    def test_create_same_vehicle(self):
        Vehicle.objects.create(**self.vehicle_data)
        url = reverse("vehicle-list")
        response = self.client.post(
            url,
            self.vehicle_payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vehicle.objects.count(), 1)

    def test_create_vehicle_with_plate_from_deactivated_vehicle(self):
        data = self.vehicle_data.copy()
        data["is_active"] = False

        Vehicle.objects.create(**data)

        url = reverse("vehicle-list")
        response = self.client.post(
            url,
            self.vehicle_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_list_vehicles(self):
        Vehicle.objects.create(**self.vehicle_data)
        url = reverse("vehicle-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_deactivated_vehicles(self):
        Vehicle.objects.create(**self.vehicle_data, is_active=False)
        url = reverse("vehicle-list")
        response = self.client.get(url, {"show": "not_active"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_all_vehicles(self):
        Vehicle.objects.create(**self.vehicle_data, is_active=False)
        new_vehicle = {
            "client": self.client_info,
            "plate":"ABC1235",
            "brand":"Toyota",
            "model":"i30",
            "year":"2020",
            "color":"branco"
        }
        Vehicle.objects.create(**new_vehicle, is_active=True)
        url = reverse("vehicle-list")
        response = self.client.get(url, {"show": "all"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_vehicle(self):
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        url = reverse("vehicle-detail", kwargs={"pk": vehicle.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], vehicle.id)

    def test_get_invalid_vehicle(self):
        url = reverse("vehicle-detail", kwargs={"pk": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_vehicle(self):
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        updated_data = {
            "client": self.client_info.id,
            "plate":"ABC1235",
            "brand":"Toyota",
            "model":"i35",
            "year":"2020",
            "color":"branco"
        }
        url = reverse("vehicle-detail", kwargs={"pk": vehicle.id})
        response = self.client.put(
            url,
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.plate, updated_data["plate"])
        self.assertEqual(vehicle.model, updated_data["model"])

    def test_update_invalid_client(self):
        updated_data = {
            "client": self.client_info.id,
            "plate":"ABC1235",
            "brand":"Toyota",
            "model":"i35",
            "year":"2020",
            "color":"branco"
        }
        url = reverse("vehicle-detail", kwargs={"pk": 1})
        response = self.client.put(
            url,
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_vehicle_with_invalid_data(self):
        vehicle = Vehicle.objects.create(**self.vehicle_data)
        updated_data = {
            "client": self.client_info.id,
            "plate":"",
            "brand":"Toyota",
            "model":"i35",
            "year":"2020",
            "color":"branco"
        }
        url = reverse("vehicle-detail", kwargs={"pk": vehicle.id})
        response = self.client.put(
            url,
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_vehicle(self):
        vehicle = Vehicle.objects.create(**self.vehicle_data)

        url = reverse(
            "vehicle-detail",
            kwargs={"pk": vehicle.id}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        vehicle.refresh_from_db()
        self.assertEqual(
            Vehicle.objects.filter(is_active=False).count(), 1
        )

    def test_transfer_vehicle_to_new_client(self):
        # Cliente atual do veículo
        vehicle = Vehicle.objects.create(**self.vehicle_data)

        # Novo proprietário
        new_client = Client.objects.create(
            name="Maria da Silva",
            email="maria@example.com",
            phone="16988888888",
            address="Rua Nova, 456",
        )

        # Desativa o veículo do proprietário antigo
        vehicle.is_active = False
        vehicle.save(update_fields=["is_active"])

        # Cria o novo registro para o novo proprietário
        new_vehicle_payload = {
            "client": new_client.id,
            "plate": vehicle.plate,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "year": vehicle.year,
            "color": vehicle.color,
        }

        url = reverse("vehicle-list")
        response = self.client.post(
            url,
            new_vehicle_payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Devemos ter dois registros históricos
        self.assertEqual(Vehicle.objects.count(), 2)

        # O veículo antigo continua vinculado ao proprietário anterior
        old_vehicle = Vehicle.objects.get(id=vehicle.id)

        self.assertEqual(old_vehicle.client, self.client_info)

        self.assertFalse(old_vehicle.is_active)

        # O novo registro pertence ao novo proprietário
        new_vehicle = Vehicle.objects.get(
            client=new_client,
            plate=vehicle.plate,
            is_active=True,
        )

        self.assertEqual(new_vehicle.client, new_client)

        self.assertTrue(new_vehicle.is_active)

        # Os dois registros representam o mesmo veículo
        self.assertEqual(new_vehicle.plate, old_vehicle.plate)