import asyncio

from django.core.management.base import BaseCommand

from bot.application import main


class Command(BaseCommand):
    help = "Run the Telegram bot (long polling or webhook)"

    def handle(self, *args, **kwargs):
        asyncio.run(main())
