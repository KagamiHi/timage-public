import logging

from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)
from imagehash import average_hash
from PIL import Image
from telethon.sync import TelegramClient, events
from telethon.tl.types import Message, MessageMediaPhoto, PeerChannel

from bot.models import SenderModel, MessageModel, ImageModel
from common.utils.async_atomic import aatomic
from django.conf import settings


@aatomic
async def process_event_data(event_message, blob):
    sender, _ = await SenderModel.objects.aget_or_create(
        channel_id=event_message.peer_id.channel_id,
    )

    category = ImageModel.ImageCategory.MAIN
    if event_message.message or event_message.grouped_id:
        category = ImageModel.ImageCategory.TEST

    image_file = ContentFile(blob)
    with Image.open(image_file) as img:
        hash = average_hash(img)
    image_file.seek(0)
    image_file.name = f"{hash}.jpg"

    image, _ = await ImageModel.objects.aget_or_create(
        hash=hash,
        defaults={"image": image_file, "category": category},
    )

    message, _ = await MessageModel.objects.aget_or_create(
        tlg_id=event_message.id,
        defaults={
            "sender": sender,
            "date": event_message.date,
            "message": event_message.message,
        },
    )
    await message.images.aadd(image)
    await message.asave()


def main():
    api_id = settings.TLG_API_ID
    api_hash = settings.TLG_API_HASH
    session_name = settings.TLG_SESSION_NAME

    with TelegramClient(session_name, api_id, api_hash) as client:
        logger.info("Catcher bot started")

        @client.on(events.NewMessage())
        async def handler(event):
            event_message = event.message

            if not isinstance(event_message, Message):
                return

            if not isinstance(event_message.peer_id, PeerChannel):
                return

            if isinstance(event_message.media, MessageMediaPhoto):
                blob = await client.download_media(event_message.media, bytes)
                await process_event_data(event_message, blob)

        client.run_until_disconnected()
