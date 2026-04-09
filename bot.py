import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование, чтобы видеть ошибки в консоли Render
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
    else:
        if value <= good_threshold: return "🟩"
        elif value <= bad_threshold: return "🟨"
        else: return "🟥"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": 1}
    await update.message.reply_text(
        "👋 Привет, этот бот поможет вам узнать статистику\n\nВведите количество убийств:"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        return

    text = update.message.text
    step = user_data[user_id]["step"]

    try:
        value = parse_input(text)
    except:
        await update.message.reply_text("Введите число!")
        return

    if step == 1:
        user_data[user_id]["K"] = value
        user_data[user_id]["step"] = 2
        await update.message.reply_text("Введите помощей:")
    elif step == 2:
        user_data[user_id]["A"] = value
        user_data[user_id]["step"] = 3
        await update.message.reply_text("Введите смерти:")
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
        data = user_data[user_id]
        
        R = data["WinR"] + data["LoseR"]
        if R == 0:
            await update.message.reply_text("Ошибка: нет раундов")
            return

        kpr = data["K"] / R
        dpr = data["D"] / R
        apr = data["A"] / R
        KD = data["K"] / data["D"] if data["D"] > 0 else data["K"]
        KAST = ((kpr + apr) * 0.7) * 100
        ADR = (data["K"] * 100 + data["A"] * 70) / R
        RS = ((kpr - 0.5) * 4 + apr * 1.2 + (data["WinR"] / R) * 2 - dpr * 2.5) * 1.5

        result = (
            f"📊 Статистика:\n\n"
            f"{get_emoji(KD, 0.9, 1.1)} K/D: {KD:.2f}\n"
            f"{get_emoji(kpr, 0.6, 0.8)} KPR: {kpr:.2f}\n"
            f"{get_emoji(dpr, 0.8, 0.6, True)} DPR: {dpr:.2f}\n"
            f"{get_emoji(ADR, 70, 90)} ADR: {ADR:.0f}\n"
            f"{get_emoji(KAST, 65, 75)} KAST: {KAST:.0f}%\n"
            f"{get_emoji(RS, 0, 1.5)} Round Swing: {RS:.2f}"
        )
        await update.message.reply_text(result)
        del user_data[user_id]

app = ApplicationBuilder().token("8647818616:AAGMjv1Jdj9lM-Gc5y4273Wnhy8WlasNB7Q").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    app.run_polling()

