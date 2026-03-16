from aiogram import Bot, Dispatcher
from django.conf import settings


tlg_bot: Bot = Bot(settings.TLG_BOT_TOKEN)
dp = Dispatcher()


async def run_webhook():
    await tlg_bot.set_webhook(
        url=f"https://{settings.EXTERNAL_HOST}/bot/telegram",
        drop_pending_updates=True,
        secret_token=settings.WEBHOOK_SECRET,
    )


async def main():
    import bot.handlers

    if settings.TLG_LONG_POLLING:
        await dp.start_polling(tlg_bot)
    else:
        await run_webhook()
