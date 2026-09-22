from rest_framework.test import APITestCase
from user.models import User

class AuthenticatedAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password = "testpassword123",
            is_staff=True,
            is_superuser=True,
        )

        self.client.force_authenticate(user=self.user)