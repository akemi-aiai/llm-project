from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.core.config import settings


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    return bot, dp
