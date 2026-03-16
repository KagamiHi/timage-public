from functools import partial
from typing import Callable

from asgiref.sync import sync_to_async
from django.db import transaction, close_old_connections


def on_commit(func: Callable, /, *args, **kwargs) -> Callable:
    return transaction.on_commit(partial(func, *args, **kwargs))  # noqa


async def aclose_old_connections():
    return await sync_to_async(close_old_connections)()
