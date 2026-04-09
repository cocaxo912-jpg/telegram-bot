import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

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
    await update.message.reply_text("🎮 **STANDOFF 2 STATS**\n\nВведите кол-во убийств (У):")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data: return
    
    text = update.message.text
    step = user_data[user_id]["step"]

    try:
        val = sum(int(p) for p in text.replace('+', ' ').split())
    except:
        await update.message.reply_text("Введите число!")
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
        await update.message.reply_text("Сколько всего раундов было в матче?\n(Например: 13 7 — это 20)")
    elif step == 5:
        user_data[user_id]["R"] = val
        d = user_data[user_id]
        
        # Расчеты на основе данных со скрина
        kd = d["K"] / d["D"] if d["D"] > 0 else d["K"]
        adr = (d["K"] * 100 + d["A"] * 70) / d["R"]
        points_per_round = d["Score"] / d["R"]
        dpr = d["D"] / d["R"]
        
        # Формула рейтинга без HS%
        rating = (kd * 0.5) + (points_per_round / 2 * 0.5)

        res = (
            f"🏆 **РЕЗУЛЬТАТ МАТЧА**\n\n"
            f"{get_emoji(kd, 0.9, 1.3)} **K/D:** {kd:.2f}\n"
            f"{get_emoji(adr, 80, 115)} **ADR:** {adr:.0f}\n"
            f"{get_emoji(points_per_round, 1.5, 2.5)} **Очков/раунд:** {points_per_round:.1f}\n"
            f"{get_emoji(dpr, 0.8, 0.65, True)} **DPR (Смертность):** {dpr:.2f}\n"
            f"-------------------\n"
            f"{get_emoji(rating, 0.8, 1.2)} **MATCH RATING:** {rating:.2f}"
        )
        
        await update.message.reply_text(res, parse_mode="Markdown")
        del user_data[user_id]

app = ApplicationBuilder().token("8647818616:AAGMjv1Jdj9lM-Gc5y4273Wnhy8WlasNB7Q").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    app.run_polling()
