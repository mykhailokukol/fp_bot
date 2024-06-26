import logging
from datetime import datetime

from pymongo import MongoClient
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler, CallbackContext

from bot.config import settings

GEO, SOURCE, VOLUME, CHECK_SUB, FINISH = range(5)

logging.basicConfig(
    format="%(levelname)s | %(name)s | %(asctime)s | %(message)s", level=logging.WARN
)
log = logging.getLogger(__name__)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Заполнить анкету", callback_data="form")],
            [
                InlineKeyboardButton(
                    "Подписаться на канал", url="https://t.me/Fonbet_Partners"
                )
            ],
        ]
    )
    await update.message.reply_text(
        "Привет!\nFonbet Partners предлагает тебе освежиться бутылочкой прохладного пива!\n\nДля этого нужно выполнить два действия:\n1. Заполнить анкету\n2. Подписаться на канал",
        reply_markup=markup,
    )


async def callback(
    update: Update,
    context: CallbackContext,
) -> int:
    query = update.callback_query
    answer = await query.answer()

    match query.data:
        case "form":
            client = MongoClient(settings.MONGODB_CLIENT_URL)
            db = client["fonbet"]
            winners = db["winners"]
            if winners.find_one({"user_id": update.effective_user.id}):
                print("found in db")
                await update.effective_chat.send_message(
                    "Вы уже получали мерч, его можно получить лишь единожды."
                )
                return
            await update.effective_chat.send_message(
                "Укажите Ваш логин в Telegram",
                reply_markup=ReplyKeyboardRemove(),
            )
            return GEO


async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """No description needed"""
    await update.message.reply_text(
        "Прекращаем последнюю операцию.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def geo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    context.user_data["username"] = update.message.text

    markup = ReplyKeyboardMarkup(
        [
            ["Россия"],
            ["Беларусь"],
            ["Казахстан"],
        ]
    )
    await update.message.reply_text(
        "Укажите с каким ГЕО Вы работаете: ",
        reply_markup=markup,
    )
    return SOURCE


async def source(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    context.user_data["geo"] = update.message.text

    await update.message.reply_text(
        "Укажите Ваш источник трафика: ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return VOLUME


async def volume(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    context.user_data["source"] = update.message.text

    await update.message.reply_text(
        "Укажите Ваш объем трафика в месяц: ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CHECK_SUB


async def check_sub(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    yes_markup = ReplyKeyboardMarkup([["Я подписался(-ась)!"]])
    if not "volume" in context.user_data:
        context.user_data["volume"] = update.message.text

    await update.message.reply_text(
        "Проверяем Вашу подписку на канал...",
        reply_markup=ReplyKeyboardRemove(),
    )
    # success_markup = ReplyKeyboardMarkup(
    #     [
    #         ["Значок"],
    #         ["Наклейки"],
    #         ["Граффити баллончик"],
    #         ["Шоппер"],
    #     ]
    # )

    chat_member = await context.bot.get_chat_member(
        chat_id=settings.CHANNEL_NAME,
        user_id=update.effective_user.id,
    )
    if chat_member.status in ["member", "administrator", "creator"]:
        await update.message.reply_text(
            "Готово\nЗабирай свой подарок на стенде B2!",
            # reply_markup=success_markup,
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data["user_id"] = update.message.from_user.id
        context.user_data["prize"] = "Пиво"
        context.user_data["datetime"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        client = MongoClient(settings.MONGODB_CLIENT_URL)
        db = client["fonbet"]
        winners = db["winners"]
        winners.insert_one(context.user_data)

        log.warn(context.user_data)

        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Вам осталось совсем немного для получения бутылочки прохладительного напитка от Fonbet Partners!\nПодпишитесь на канал https://t.me/Fonbet_Partners",
            reply_markup=yes_markup,
        )
        return CHECK_SUB
