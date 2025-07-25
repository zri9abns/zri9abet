import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import datetime

# 🔐 توكن البوت
TOKEN = "7508194187:AAGOgYJI_aSywxCsO4gtmCo3NxQLa9XFS8Y"
CHANNEL_USERNAME = "zri9abet"

# إعداد اللوج
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🎯 جلب التوقعات بتنسيق مرتب + الأودز
def get_predictions():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://bankerpredict.com/?dt={today}"

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr")[1:]

        if not rows:
            return "❌ لم يتم العثور على توقعات اليوم."

        predictions = ""
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:  # تأكد من وجود odds
                time = cols[0].text.strip()
                league = cols[1].text.strip()
                match = cols[2].text.strip()
                tip = cols[3].text.strip()
                odds = cols[4].text.strip()

                predictions += (
                    f"🕓 {time} | 🏆 {league}\n"
                    f"⚔️ {match}\n"
                    f"🎯 التوقع: {tip}\n"
                    f"💸 الأودز: {odds}\n"
                    f"━━━━━━━━━━━━━━\n"
                )

        return predictions.strip()

    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        return "⚠️ وقعات شي مشكل فالإتصال بالموقع."

# ✅ التحقق من الاشتراك
async def is_user_subscribed(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.warning(f"Subscription check failed: {e}")
        return False

# 🚀 أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✅ نعم، أريد التوقعات", callback_data="yes_first")]]
    today = datetime.datetime.now().strftime("%A, %d %B %Y")
    await update.message.reply_text(
        f"👋🏻 مرحباً بك!\n\n📅 تاريخ اليوم: {today}\nهل ترغب في التوقعات المضمونة؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ⌨️ التعامل مع الضغط
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "yes_first":
        is_sub = await is_user_subscribed(context, query.from_user.id)
        if is_sub:
            predictions = get_predictions()
            if len(predictions) > 4000:
                for i in range(0, len(predictions), 4000):
                    await query.message.reply_text(predictions[i:i+4000])
            else:
                await query.message.reply_text(predictions)
        else:
            keyboard = [
                [InlineKeyboardButton("📢 إشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("✅ نعم، إشتركت", callback_data="confirm_sub")]
            ]
            await query.message.reply_text(
                f"❌ خاصك تشترك فالقناة:\nhttps://t.me/{CHANNEL_USERNAME}\n\nمن بعد، اضغط نعم ✅",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif query.data == "confirm_sub":
        is_sub = await is_user_subscribed(context, query.from_user.id)
        if is_sub:
            predictions = get_predictions()
            if len(predictions) > 4000:
                for i in range(0, len(predictions), 4000):
                    await query.message.reply_text(predictions[i:i+4000])
            else:
                await query.message.reply_text(predictions)
        else:
            await query.message.reply_text("❌ مزال ما إشتركتش، جرب من جديد من بعد ما تشترك.")

# ▶️ تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    logger.info("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
