from unittest.mock import patch
from django.conf import settings
from rest_framework import status

from bot.models import ImageModel, Reaction
from common.tests import AuthClientSetUpMixin, CustomTestCase
from users.models import User


class TestImageExternalUrl(CustomTestCase):
    def test_url_format(self):
        img = ImageModel(image="my-photo.jpg", hash="abc", category=ImageModel.ImageCategory.MAIN)
        expected = f"{settings.CDN_EXTERNAL_ENDPOINT}/{settings.IMAGES_BUCKET}/my-photo.jpg"
        self.assertEqual(img.external_url, expected)


class TestReactionDeduplication(CustomTestCase):
    def setUp(self):
        self.user = self.make_user(tlg_id=100)
        self.image = self.make_image("h1")

    def test_creates_reaction(self):
        Reaction.objects.update_or_create(user=self.user, image=self.image, defaults={"react": True})
        self.assertEqual(Reaction.objects.filter(user=self.user, image=self.image).count(), 1)

    def test_updates_not_duplicates(self):
        Reaction.objects.create(user=self.user, image=self.image, react=True)
        Reaction.objects.update_or_create(user=self.user, image=self.image, defaults={"react": False})
        r = Reaction.objects.get(user=self.user, image=self.image)
        self.assertFalse(r.react)
        self.assertEqual(Reaction.objects.filter(user=self.user, image=self.image).count(), 1)


class TestSwipesList(AuthClientSetUpMixin):
    tlg_id = 101

    def setUp(self):
        super().setUp()
        self.image = self.make_image("h2")

    def test_unauthenticated_returns_401(self):
        response = self.anonymous_client.get("/api/swipes/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_main_images(self):
        response = self.auth_client.get("/api/swipes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(str(self.image.id), ids)

    def test_excludes_reacted_images(self):
        Reaction.objects.create(user=self.user, image=self.image, react=True)
        response = self.auth_client.get("/api/swipes/")
        ids = [item["id"] for item in response.data]
        self.assertNotIn(str(self.image.id), ids)

    def test_excludes_test_category(self):
        test_img = self.make_image("h_test", category=ImageModel.ImageCategory.TEST)
        response = self.auth_client.get("/api/swipes/")
        ids = [item["id"] for item in response.data]
        self.assertNotIn(str(test_img.id), ids)


class TestSwipesReact(AuthClientSetUpMixin):
    tlg_id = 102

    def setUp(self):
        super().setUp()
        self.image = self.make_image("h3")
        self.url = f"/api/swipes/{self.image.id}/react/"

    def test_unauthenticated_returns_401(self):
        response = self.anonymous_client.post(self.url, {"react": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch.object(User, "send_tlg_message")
    def test_like_creates_reaction_and_sends_message(self, mock_send):
        response = self.auth_client.post(self.url, {"react": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Reaction.objects.filter(user=self.user, image=self.image, react=True).exists())
        mock_send.assert_called_once_with(self.image)

    @patch.object(User, "send_tlg_message")
    def test_dislike_does_not_send_message(self, mock_send):
        response = self.auth_client.post(self.url, {"react": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_send.assert_not_called()

    @patch.object(User, "send_tlg_message", side_effect=Exception("network error"))
    def test_telegram_error_returns_500(self, _mock_send):
        response = self.auth_client.post(self.url, {"react": True}, format="json")
        self.assertEqual(response.status_code, 500)

    @patch.object(User, "send_tlg_message")
    def test_react_update_no_duplicate(self, _mock_send):
        Reaction.objects.create(user=self.user, image=self.image, react=True)
        self.auth_client.post(self.url, {"react": False}, format="json")
        r = Reaction.objects.get(user=self.user, image=self.image)
        self.assertFalse(r.react)
        self.assertEqual(Reaction.objects.filter(user=self.user, image=self.image).count(), 1)
