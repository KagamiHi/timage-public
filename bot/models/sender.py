from django.db import models
from common.models import UUIDModel


class SenderModel(UUIDModel):
    channel_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)