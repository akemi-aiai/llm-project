import asyncio
import logging

from app.bot.dispatcher import create_bot_and_dispatcher

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot, dp = create_bot_and_dispatcher()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
