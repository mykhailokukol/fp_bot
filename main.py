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
from bot.base import (
    cancel,
    start,
    # callback,
    geo,
    source,
    # language,
    check_sub,
    # finish,
    action,
    username,
)
from bot.base import ACTION, USERNAME, GEO, SOURCE, CHECK_SUB

logging.basicConfig(
    format="%(levelname)s | %(name)s | %(asctime)s | %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)


def main() -> None:
    print("Starting...")
    app = ApplicationBuilder().token(settings.TG_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, action)],
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username)],
            GEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, geo)],
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, source)],
            CHECK_SUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_sub)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(conv_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
