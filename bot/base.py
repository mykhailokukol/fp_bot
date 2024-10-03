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


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    print("start")
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
        "Привет!\nЧтобы поучаствовать в розыгрыше от Fonbet Partners нужно выполнить 2 условия:\n1. Заполнить анкету\n2. Подписаться на канал",
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
                    "Вы уже участвуете в розыгрыше."
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

    # markup = ReplyKeyboardMarkup(
    #     [
    #         ["Россия"],
    #         ["Беларусь"],
    #         ["Казахстан"],
    #     ]
    # )
    await update.message.reply_text(
        "Вертикаль, с которой работаешь:",
        # reply_markup=markup,
    )
    return SOURCE


async def source(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    context.user_data["vertical"] = update.message.text

    markup = ReplyKeyboardMarkup(
        [
            ["Хочу"],
            ["Не хочу"],
        ]
    )

    await update.message.reply_text(
        "Хочу участвовать в розыгрыше:",
        reply_markup=markup,
    )
    return CHECK_SUB


async def volume(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:

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
    if not "will" in context.user_data:
        context.user_data["will"] = update.message.text

    await update.message.reply_text(
        "Проверяем Вашу подписку на канал...",
        reply_markup=ReplyKeyboardRemove(),
    )
    success_markup = ReplyKeyboardMarkup(
        [
            ["Стикерпак"],
            ["Шнурочек для телефона"],
            ["Брелок"],
            ["Шоппер"],
        ]
    )

    chat_member = await context.bot.get_chat_member(
        chat_id=settings.CHANNEL_NAME,
        user_id=update.effective_user.id,
    )
    if chat_member.status in ["member", "administrator", "creator"]:
        await update.message.reply_text(
            "Готово, вы участник розыгрыша!",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["OK"],
                ]
            ),
        )
        return FINISH
    else:
        await update.message.reply_text(
            "Для участия в розыгрыше Вам осталось совсем немного\nПодпишитесь на канал https://t.me/Fonbet_Partners",
            reply_markup=yes_markup,
        )
        return CHECK_SUB


async def finish(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    context.user_data["user_id"] = update.message.from_user.id
    # context.user_data["prize"] = update.message.text
    context.user_data["datetime"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    client = MongoClient(settings.MONGODB_CLIENT_URL)
    db = client["fonbet"]
    winners = db["winners"]
    winners.insert_one(context.user_data)
    print(context.user_data)

    await update.message.reply_text(
        "Готово ✅\nЖди результатов на стенде K1, спасибо за участие!",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END
