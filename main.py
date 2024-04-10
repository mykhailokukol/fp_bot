import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from bot.config import settings
from bot.base import cancel, start, callback, geo, source, volume, check_sub, finish
from bot.base import GEO, SOURCE, VOLUME, CHECK_SUB, FINISH

logging.basicConfig(
    format="%(levelname)s | %(name)s | %(asctime)s | %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)


def main() -> None:
    print("Starting...")
    app = ApplicationBuilder().token(settings.TG_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback, pattern="form")],
        states={
            GEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, geo)],
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, source)],
            VOLUME: [MessageHandler(filters.TEXT & ~filters.COMMAND, volume)],
            CHECK_SUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_sub)],
            FINISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(conv_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
