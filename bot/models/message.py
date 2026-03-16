from django.db import models
from common.models import UUIDModel


class MessageModel(UUIDModel):
    tlg_id = models.BigIntegerField(unique=True)
    sender = models.ForeignKey("SenderModel", on_delete=models.CASCADE)
    date = models.DateTimeField()
    message = models.TextField()
    images = models.ManyToManyField("ImageModel")
    created_at = models.DateTimeField(auto_now_add=True)