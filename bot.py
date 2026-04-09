import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

user_data = {}

def get_emoji(value, bad, good, reverse=False):
    if not reverse:
        if value >= good: return "🟩"
        elif value >= bad: return "🟨"
        else: return "🟥"
    else:
        if value <= good: return "🟩"
        elif value <= bad: return "🟨"
        else: return "🟥"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": 1}
    text = "🎮 **STANDOFF 2 STATS**\n\nВведите кол-во убийств (У):"
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.callback_query.message.reply_text(text, parse_mode="Markdown")

async def restart_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "restart_calc":
        await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data: return
    msg_text = update.message.text.strip()
    step = user_data[user_id]["step"]

    if step == 5:
        if not msg_text.isdigit():
            await update.message.reply_text("❌ Введите одно целое число (например: 20)")
            return
        val = int(msg_text)
    else:
        try:
            val = sum(int(p) for p in msg_text.replace('+', ' ').split())
        except:
            await update.message.reply_text("❌ Введите число!")
            return

    if step == 1:
        user_data[user_id]["K"] = val
        user_data[user_id]["step"] = 2
        await update.message.reply_text("Введите помощи (П):")
    elif step == 2:
        user_data[user_id]["A"] = val
        user_data[user_id]["step"] = 3
        await update.message.reply_text("Введите смерти (С):")
    elif step == 3:
        user_data[user_id]["D"] = val
        user_data[user_id]["step"] = 4
        await update.message.reply_text("Введите ваш 'Счёт' из таблицы:")
    elif step == 4:
        user_data[user_id]["Score"] = val
        user_data[user_id]["step"] = 5
        await update.message.reply_text("Введите общее количество раундов:")
    elif step == 5:
        user_data[user_id]["R"] = val
        d = user_data[user_id]
        kd = d["K"] / d["D"] if d["D"] > 0 else d["K"]
        adr = (d["K"] * 100 + d["A"] * 70) / d["R"]
        ppr = d["Score"] / d["R"]
        dpr = d["D"] / d["R"]
        fire = (adr * 0.8) + ((d["K"]/d["R"]) * 20)
        rating = (kd * 0.5) + (ppr / 2 * 0.5)

        res = (
            f"🏆 **РЕЗУЛЬТАТ МАТЧА**\n\n"
            f"{get_emoji(kd, 0.9, 1.3)} **K/D:** {kd:.2f}\n"
            f"{get_emoji(adr, 80, 115)} **ADR:** {adr:.0f}\n"
            f"{get_emoji(fire, 90, 125)} **FIREPOWER:** {fire:.0f}\n"
            f"{get_emoji(ppr, 1.5, 2.5)} **Очков/раунд:** {ppr:.1f}\n"
            f"{get_emoji(dpr, 0.8, 0.65, True)} **DPR:** {dpr:.2f}\n"
            f"-------------------\n"
            f"{get_emoji(rating, 0.8, 1.2)} **MATCH RATING:** {rating:.2f}"
        )
        keyboard = [[InlineKeyboardButton("🔄 Начать заново", callback_data="restart_calc")]]
        await update.message.reply_text(res, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        del user_data[user_id]

# Запуск
token = "8647818616:AAGMjv1Jdj9lM-Gc5y4273Wnhy8WlasNB7Q"
app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(restart_button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    app.run_polling()
