"""
Playground script example.

Run from the project root:
    uv run playground/base.py

Or copy this file and run your own script:
    cp playground/base.py playground/my_script.py
    uv run playground/my_script.py
"""
import _setup

from users.models import User
from bot.models import ImageModel

# Example: list users
for user in User.objects.all():
    print(user.tlg_id, user.tlg_username)

# Example: count images
print("Images:", ImageModel.objects.count())
