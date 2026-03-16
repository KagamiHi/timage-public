from django.core.management.base import BaseCommand

from bot.catcher import main


class Command(BaseCommand):
    help = "Run the Telethon catcher bot"

    def handle(self, *args, **kwargs):
        main()
