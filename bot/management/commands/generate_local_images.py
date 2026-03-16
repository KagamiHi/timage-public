import io
import logging

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from imagehash import average_hash
from PIL import Image

from bot.models import ImageModel, Reaction

logger = logging.getLogger(__name__)

COLORS = [
    ("red", (220, 50, 50)),
    ("green", (50, 180, 50)),
    ("blue", (50, 100, 220)),
    ("yellow", (230, 200, 50)),
    ("purple", (150, 50, 200)),
]


class Command(BaseCommand):
    help = "Generate 5 solid-color placeholder images for local development"

    def handle(self, *args, **kwargs):
        for i, (name, rgb) in enumerate(COLORS):
            img = Image.new("RGB", (512, 512))
            pixels = img.load()
            for x in range(512):
                for y in range(512):
                    factor = 1 - y / 511
                    pixels[x, y] = tuple(int(c * factor) for c in rgb)
            # unique white block per image so average_hash differs
            block = (i + 1) * 64
            for x in range(block):
                for y in range(block):
                    pixels[x, y] = (255, 255, 255)
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            buf.seek(0)
            hash_val = average_hash(img)
            file = ContentFile(buf.read(), name=f"{hash_val}.jpg")
            image, created = ImageModel.objects.get_or_create(
                hash=str(hash_val),
                defaults={"image": file, "category": ImageModel.ImageCategory.MAIN},
            )
            if created:
                logger.info("%s: created", name)
            else:
                deleted, _ = Reaction.objects.filter(image=image).delete()
                logger.info("%s: already exists, deleted %d reactions", name, deleted)
