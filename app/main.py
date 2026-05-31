import asyncio
import logging

from app.bot.bot import create_bot, create_dispatcher
from app.core.config import settings


logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Starting bot application")

    bot = create_bot()
    dp = create_dispatcher()

    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Closing bot session")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
