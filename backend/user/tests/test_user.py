from django.urls import reverse

from rest_framework import status

from backend.tests.base import AuthenticatedAPITestCase
from user.models import User, UserInvitation


class UserAPITestCase(AuthenticatedAPITestCase):

    def test_create_user(self):
        data = {
            "email": "joao@example.com",
            "address": "Rua das Flores, 123",
            "phone": "16999999999",
        }

        url = reverse("user-list")

        response = self.client.post(url, data, format="json",)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED,)
        self.assertEqual(User.objects.count(), 2,)

        user = User.objects.get(email="joao@example.com")

        self.assertTrue(user.has_usable_password() is False)
        self.assertIsNone(user.activated_at)
        self.assertEqual(UserInvitation.objects.filter(user=user).count(), 1)
        self.assertTrue(response.data["invitation_token"])

    def test_create_user_does_not_accept_password(self):
        data = {
            "email": "maria@example.com",
            "address": "Rua Nova, 456",
            "phone": "16988888888",
            "password": "MinhaSenha123!",
        }
        url = reverse("user-list")
        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED,)

        user = User.objects.get(email="maria@example.com")

        self.assertFalse(user.has_usable_password())

    def test_create_same_user(self):
        User.objects.create_user(
            email="joao@example.com",
            password = "testpassword123",
            address = "Rua das Flores, 123",
            phone = "16999999999",
        )
        data = {
            "email": "joao@example.com",
            "address": "Rua das Flores, 123",
            "phone": "16999999999",
        }

        url = reverse("user-list")

        response = self.client.post(url, data, format="json",)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,)
        self.assertEqual(User.objects.count(), 2,)

    def test_list_users(self):
        User.objects.create_user(
            email="joao@example.com",
            password = "testpassword123",
            address = "Rua das Flores, 123",
            phone = "16999999999",
        )
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_deactivated_users(self):
        User.objects.create_user(
            email="joao@example.com",
            password = "testpassword123",
            address = "Rua das Flores, 123",
            phone = "16999999999",
            active = False,
        )
        url = reverse("user-list")
        response = self.client.get(url, {"show": "not_active"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_all_users(self):
        User.objects.create_user(
            email="joao@example.com",
            password = "testpassword123",
            address = "Rua das Flores, 123",
            phone = "16999999999",
            active = False,
        )
        User.objects.create_user(
            email="julio@example.com",
            password = "testpassword123",
            address = "Rua das arvores, 123",
            phone = "16999999998",
            active = True,
        )
        url = reverse("user-list")
        response = self.client.get(url, {"show": "all"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_user(self):
        user = User.objects.create_user(
            email="julio@example.com",
            password = "testpassword123",
            address = "Rua das arvores, 123",
            phone = "16999999998",
            active = True,
        )
        url = reverse("user-detail", kwargs={"pk": user.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], user.id)

    def test_get_invalid_user(self):
        url = reverse("user-detail", kwargs={"pk": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user(self):
        user = User.objects.create_user(
            email="julio@example.com",
            password = "testpassword123",
            address = "Rua das arvores, 123",
            phone = "16999999998",
            active = True,
        )
        updated_data = {
            "first_name": "Julio",
            "email": "julio@example.com",
            "address": "Rua das arvores, 123",
            "phone": "16999999998"
        }
        url = reverse("user-detail", kwargs={"pk": user.id})
        response = self.client.put(
            url,
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, updated_data["first_name"])

    def test_update_invalid_user(self):
        updated_data = {
            "first_name": "João"
        }
        url = reverse("user-detail", kwargs={"pk": 1})
        response = self.client.put(
            url,
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user(self):
        user = User.objects.create_user(
            email="julio@example.com",
            password = "testpassword123",
            address = "Rua das arvores, 123",
            phone = "16999999998",
            active = True,
        )

        url = reverse(
            "user-detail",
            kwargs={"pk": user.id}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(
            User.objects.filter(active=False).count(), 1
        )