from celery import shared_task

from bot.utils.recommendation import precompute_pca_and_save


@shared_task
def prepare_recommendations_valuables():
    precompute_pca_and_save()

@shared_task
def manage_tlg_subscriptions():
    from telethon.sync import TelegramClient
    from django.conf import settings
    api_id = settings.TLG_API_ID
    api_hash = settings.TLG_API_HASH
    session_name = settings.TLG_SESSION_NAME
    with TelegramClient(session_name, api_id, api_hash) as client:
        client.loop.run_until_complete(
            client.send_message("me", "✅ Celery task `manage_tlg_subscriptions` is running.")
        )
