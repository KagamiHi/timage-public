from typing import Union

import requests
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.cache import cache
from django.db import models
from aiogram.types import User as TlgUser

from common.utils.async_atomic import aatomic
from bot.utils.recommendation import recommend_images_for_user
from common.models.uuid import UUIDModel


class UserManager(BaseUserManager):
    def create_user(self, tlg_id, **extra_fields):
        extra_fields.setdefault("is_active", True)
        user = self.model(tlg_id=tlg_id, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, tlg_id, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(tlg_id, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, UUIDModel):
    tlg_id = models.BigIntegerField(unique=True)
    tlg_username = models.TextField(null=True, blank=True)
    language_code = models.TextField(default="en")
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "tlg_id"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @classmethod
    @aatomic
    async def aget_or_create_from_tlg(cls, chat_id: int) -> tuple["User", bool]:
        return await cls.objects.aupdate_or_create(tlg_id=chat_id)

    @classmethod
    def patch_telegram_data(cls, user_data: Union[TlgUser, dict]) -> dict:
        field_names = {f.name for f in cls._meta.fields}
        if isinstance(user_data, TlgUser):
            user_data = {f: getattr(user_data, f, None) for f in field_names}
        data = {k: v for k, v in user_data.items() if v is not None and k in field_names}
        data["tlg_username"] = user_data.get("username")
        return data

    def send_tlg_message(self, image_obj):
        if self.is_staff:
            return
        url = f"https://api.telegram.org/bot{settings.TLG_BOT_TOKEN}/sendPhoto"
        response = requests.post(
            url,
            json={"chat_id": self.tlg_id, "photo": image_obj.external_url},
            timeout=5,
        )
        response.raise_for_status()

    def recommend_for_user(self, limit=10):
        from bot.models import Reaction, ImageModel

        default_user_ratio = settings.DEFAULT_USER_RECOMMENDATION_RATIO
        is_premium = getattr(self, "is_premium", False)
        recommendations_limit = limit if is_premium else int(limit * default_user_ratio)

        seen_images = set(
            img_id.hex
            for img_id in Reaction.objects.filter(user=self).values_list(
                "image_id", flat=True
            )
        )

        last_batch = cache.get(f"user_batch:{self.id}") or []
        seen_images.update(last_batch)

        recommended_images = ImageModel.objects.none()
        recommended_images_for_user = recommend_images_for_user(self)

        unseen_image_ids = []
        for img_id in recommended_images_for_user:
            if img_id not in seen_images:
                unseen_image_ids.append(img_id)
                if len(unseen_image_ids) >= recommendations_limit:
                    break

        if unseen_image_ids:
            recommended_images = ImageModel.objects.filter(id__in=unseen_image_ids)

        recommended_count = recommended_images.count()
        remaining_limit = limit - recommended_count
        fallback_images = (
            ImageModel.objects.filter(category=ImageModel.ImageCategory.MAIN)
            .exclude(id__in=seen_images)
            .order_by("-created_at")[:remaining_limit]
        )
        return recommended_images | fallback_images
