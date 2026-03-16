import uuid6

from django.db import models


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)

    class Meta:
        abstract = True

    @classmethod
    def filter_fields(cls, fields: dict) -> dict:
        allowed_fields = [f.name for f in cls._meta.fields]
        return {k: v for k, v in fields.items() if k in allowed_fields}

    def update(self, **kwargs):
        if self._state.adding:
            raise self.DoesNotExist
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save(update_fields=kwargs.keys())

    async def aupdate(self, **kwargs):
        if self._state.adding:
            raise self.DoesNotExist
        for field, value in kwargs.items():
            setattr(self, field, value)
        await self.asave(update_fields=kwargs.keys())
