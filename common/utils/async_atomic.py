from asgiref.sync import sync_to_async
from django.db import transaction


class AsyncAtomic:
    def __init__(self, using=None, savepoint=True, durable=True):
        self.using = using
        self.savepoint = savepoint
        self.durable = durable

    async def __aenter__(self):
        self.atomic = transaction.Atomic(self.using, self.savepoint, self.durable)
        await sync_to_async(self.atomic.__enter__)()
        return self.atomic

    async def __aexit__(self, exc_type, exc_value, traceback):
        await sync_to_async(self.atomic.__exit__)(exc_type, exc_value, traceback)


def aatomic(fun):
    async def wrapper(*args, **kwargs):
        async with AsyncAtomic():
            return await fun(*args, **kwargs)

    return wrapper
