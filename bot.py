# telegram-bot

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

user_data = {}

def parse_input(value):
    if not value.strip():
        return 0
    parts = value.replace('+', ' ').split()
    return sum(int(part) for part in parts)

def get_emoji(value, bad_threshold, good_threshold, reverse=False):
    if not reverse:
        if value >= good_threshold: return "🟩"
        elif value >= bad_threshold: return "🟨"
        else: return "🟥"
    else: # Для смертей: чем меньше, тем лучше
        if value <= good_threshold: return "🟩"
        elif value <= bad_threshold: return "🟨"
        else: return "🟥"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"step": 1}
    await update.message.reply_text(
        "👋 Привет, этот бот поможет вам узнать вашу статистику за матч\n\nВведите количество убийств:"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_data:
        await update.message.reply_text("Напиши /start")
        return

    step = user_data[user_id]["step"]

    try:
        value = parse_input(text)
    except:
        await update.message.reply_text("Введите число!")
        return

    if step == 1:
        user_data[user_id]["K"] = value
        user_data[user_id]["step"] = 2
        await update.message.reply_text("Введите количество помощей:")

    elif step == 2:
        user_data[user_id]["A"] = value
        user_data[user_id]["step"] = 3
        await update.message.reply_text("Введите количество смертей:")

    elif step == 3:
        user_data[user_id]["D"] = value
        user_data[user_id]["step"] = 4
        await update.message.reply_text("Введите проигранные раунды:")

    elif step == 4:
        user_data[user_id]["LoseR"] = value
        user_data[user_id]["step"] = 5
        await update.message.reply_text("Введите выигранные раунды:")

    elif step == 5:
        user_data[user_id]["WinR"] = value

        K = user_data[user_id]["K"]
        A = user_data[user_id]["A"]
        D = user_data[user_id]["D"]
        wins = user_data[user_id]["WinR"]
        losses = user_data[user_id]["LoseR"]

        R = wins + losses
        if R == 0:
            await update.message.reply_text("Ошибка: нет раундов")
            return

        kpr = K / R
        dpr = D / R
        apr = A / R
        KD = K / D if D > 0 else K

        KAST = ((kpr + apr) * 0.7) * 100
        ADR = (K * 100 + A * 70) / R

        RS = ((kpr - 0.5) * 4 + apr * 1.2 + (wins / R) * 2 - dpr * 2.5) * 1.5

