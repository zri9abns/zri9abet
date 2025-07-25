import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from bs4 import BeautifulSoup
import requests
import datetime

# إعدادات اللوج
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# توكن البوت
TOKEN = "7508194187:AAGOgYJI_aSywxCsO4gtmCo3NxQLa9XFS8Y"

# اسم القناة بدون @
CHANNEL_USERNAME = "zri9abet"

# ✅ جلب توقعات اليوم فقط
def get_today_predictions():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://bankerpredict.com/?dt={today_str}"

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")

        if not table:
            return "❌ لا توجد توقعات لليوم."

        rows = table.find_all("tr")[1:]  # تجاوز العناوين
        predictions = "🎯 توقعات اليوم:\n\n"

        for row in rows[:10]:  # خذ فقط أول 10 توقعات
            cells = row.find_all("td")
            if len(cells) >= 4:
                time = cells[0].text.strip()
                league = cells[1].text.strip()
                match = cells[2].text.strip()
                tip = cells[3].text.strip()
                predictions += f"🕒 {time} | 🏆 {league}\n⚽ {match} | 🎯 {tip}\n\n"

        if len(predictions) > 4096:
            predictions = predictions[:4090] + "\n... 📉 تم تقليص عدد التوقعات."

        return predictions.strip()

    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        return "❌ وقع مشكل فجلب التوقعات."

# ✅ التحقق من الاشتراك
async def is_user_subscribed(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Subscription check failed: {e}")
        return False

# ✅ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ نعم، أريد التوقعات", callback_data="yes_first")]
    ]
    await update.message.reply_text(
        "👋🏻 مرحباً بك!\n\n✅ واش بغيتي توقعات اليوم؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ✅ الضغط على الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "yes_first":
        is_sub = await is_user_subscribed(context, query.from_user.id)
        if is_sub:
            predictions = get_today_predictions()
            await query.edit_message_text(predictions)
        else:
            keyboard = [
                [InlineKeyboardButton("📢 إشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("✅ نعم، إشتركت", callback_data="confirm_sub")]
            ]
            await query.edit_message_text(
                f"❌ خاصك تشترك فالقناة:\nhttps://t.me/{CHANNEL_USERNAME}\n\n📌 من بعد الاشتراك، ضغط على نعم ✅",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif query.data == "confirm_sub":
        is_sub = await is_user_subscribed(context, query.from_user.id)
        if is_sub:
            predictions = get_today_predictions()
            await query.edit_message_text(predictions)
        else:
            await query.edit_message_text("❌ مزال ما اشتركتش، جرب من جديد من بعد الاشتراك.")

# ✅ إطلاق البوت
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    logger.info("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
