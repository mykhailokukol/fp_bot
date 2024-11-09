from datetime import datetime

from pymongo import MongoClient
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import settings
from bot.translations import (
    action_tr,
    username_tr,
    geo_tr,
    source_tr,
    check_sub_tr,
    cancel_tr,
)

ACTION, USERNAME, GEO, SOURCE, CHECK_SUB = range(5)


client = MongoClient(settings.MONGODB_CLIENT_URL)
db = client["fonbet"]
WINNERS_TABLE = db["winners"]


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """start"""
    print(f"DEBUG: Start triggered from: {update.message.from_user.id}")

    # Look for user on DB
    if WINNERS_TABLE.find_one({"user_id": update.message.from_user.id}):
        await update.message.reply_text(
            "Вы уже участвуете в розыграше.\nYou are already took a part in the giveaway."
        )
        return

    markup = ReplyKeyboardMarkup(
        [
            ["Русский"],
            ["English"],
        ]
    )
    await update.message.reply_text(
        "Выберите язык:\nChoose your language:",
        reply_markup=markup,
    )

    return ACTION


async def action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """action"""
    print(f"DEBUG: Action triggered from: {update.message.from_user.id}")

    text = update.message.text
    if text not in ["Русский", "English"]:
        await update.message.reply_text(
            "Ошибка. Выберите язык, нажав на кнопку.\nError. Please choose your language pressing button below.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return await start(update, context)
    else:
        if text == "English":
            text = text.lower()
        else:
            text = "russian"
    context.user_data["language"] = text

    markup2 = ReplyKeyboardMarkup(
        [
            [action_tr[context.user_data["language"]]["fill_form"]],
        ]
    )
    await update.message.reply_text(
        action_tr[context.user_data["language"]]["action"],
        reply_markup=markup2,
    )
    markup1 = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=action_tr[context.user_data["language"]]["subscribe"],
                    url="https://t.me/Partners_Batery",
                ),
            ],
        ],
    )
    await update.message.reply_text(
        action_tr[context.user_data["language"]]["subscribe_text"],
        reply_markup=markup1,
    )

    return USERNAME


async def username(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """username"""
    print(f"DEBUG: Username triggered from: {update.message.from_user.id}")

    await update.message.reply_text(
        username_tr[context.user_data["language"]],
        reply_markup=ReplyKeyboardRemove(),
    )

    return GEO


async def geo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """geo"""
    print(f"DEBUG: Geo triggered from: {update.message.from_user.id}")

    context.user_data["username"] = update.message.text

    await update.message.reply_text(
        geo_tr[context.user_data["language"]],
        reply_markup=ReplyKeyboardRemove(),
    )

    return SOURCE


async def source(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """source"""
    print(f"DEBUG: Source triggered from: {update.message.from_user.id}")

    context.user_data["geo"] = update.message.text

    await update.message.reply_text(
        source_tr[context.user_data["language"]],
        reply_markup=ReplyKeyboardRemove(),
    )

    return CHECK_SUB


async def check_sub(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """check_sub"""
    print(f"DEBUG: Check Sub triggered from: {update.message.from_user.id}")

    if not "source" in context.user_data:
        # Don't save "source" if user here when unsubscribed
        context.user_data["source"] = update.message.text

    await update.message.reply_text(
        check_sub_tr[context.user_data["language"]]["check"],
        reply_markup=ReplyKeyboardRemove(),
    )

    chat_member = await context.bot.get_chat_member(
        chat_id=settings.CHANNEL_NAME,
        user_id=update.effective_user.id,
    )

    if chat_member.status in ["member", "administrator", "creator"]:
        await update.message.reply_text(
            check_sub_tr[context.user_data["language"]]["success"],
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await update.message.reply_text(
            check_sub_tr[context.user_data["language"]]["failure"],
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["OK"],
                ]
            ),
        )
        return CHECK_SUB

    context.user_data["user_id"] = update.message.from_user.id
    context.user_data["date_time"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    # Save to the DB
    WINNERS_TABLE.insert_one(context.user_data)
    print(context.user_data)
    return ConversationHandler.END


async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """No description needed"""
    try:
        text = cancel_tr[context.user_data["language"]]
    except KeyError:
        text = "Cancel."

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END
