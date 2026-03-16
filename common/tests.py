from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from bot.models import ImageModel
from users.models import User


class CustomTestCase(TestCase):
    @staticmethod
    def make_user(tlg_id, **kwargs) -> User:
        return User.objects.create_user(tlg_id=tlg_id, **kwargs)

    @staticmethod
    def make_image(hash_val, category=ImageModel.ImageCategory.MAIN) -> ImageModel:
        return ImageModel.objects.create(hash=hash_val, image="test.jpg", category=category)

    @staticmethod
    def get_jwt(user: User) -> str:
        return str(RefreshToken.for_user(user).access_token)


class AuthClientSetUpMixin(CustomTestCase):
    tlg_id = 1

    def setUp(self):
        super().setUp()
        self.user = self.make_user(tlg_id=self.tlg_id)
        self.auth_client = APIClient()
        self.auth_client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.get_jwt(self.user)}")
        self.anonymous_client = APIClient()


class HealthCheckTestCase(CustomTestCase):
    def test_health_check(self):
        response = APIClient().get("/health/")
        self.assertEqual(response.status_code, 200)
