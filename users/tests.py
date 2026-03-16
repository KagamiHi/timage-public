from bot.models import ImageModel, Reaction
from common.tests import CustomTestCase

class TestRecommendForUser(CustomTestCase):
    def setUp(self):
        self.user = self.make_user(tlg_id=300)

    def test_returns_main_images(self):
        img = self.make_image("rec_h1")
        result = list(self.user.recommend_for_user())
        self.assertIn(img, result)

    def test_excludes_reacted_images(self):
        img = self.make_image("rec_h2")
        Reaction.objects.create(user=self.user, image=img, react=True)
        result = list(self.user.recommend_for_user())
        self.assertNotIn(img, result)

    def test_excludes_test_category(self):
        test_img = self.make_image("rec_h3", category=ImageModel.ImageCategory.TEST)
        result = list(self.user.recommend_for_user())
        self.assertNotIn(test_img, result)

    def test_respects_limit(self):
        for i in range(15):
            self.make_image(f"rec_limit_{i}")
        result = list(self.user.recommend_for_user(limit=5))
        self.assertLessEqual(len(result), 5)
