from django.db import models
from django_minio_backend import MinioBackend

from django.conf import settings
from common.models import UUIDModel


class ImageModel(UUIDModel):
    class ImageCategory(models.TextChoices):
        TEST = "test", "Test"
        MAIN = "main", "Main (Visible to All)"

    image = models.ImageField(storage=MinioBackend(bucket_name="images"))
    hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(
        max_length=10, choices=ImageCategory.choices, default=ImageCategory.TEST
    )

    @property
    def external_url(self) -> str:
        return f"{settings.CDN_EXTERNAL_ENDPOINT}/{settings.IMAGES_BUCKET}/{self.image.name}"
