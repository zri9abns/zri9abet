import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import datetime

TOKEN = "7508194187:AAGrDyChNR2Wc6q4wIzSOrmD4baSNfdvJBk"
CHANNEL_USERNAME = "zri9abet"

logging.basicConfig(level=logging.INFO)

# جلب التوقعات من focuspredict
def get_predictions():
    url = "https://focuspredict.com/all-soccer-predictions"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return "❌ تعذر جلب التوقعات حالياً."

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if not table:
        return "❌ لم يتم العثور على التوقعات."

    rows = table.find_all("tr")[1:]
    predictions = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5:
            time = cols[0].text.strip()
            league = cols[1].text.strip()
            match = cols[2].text.strip()
            tip = cols[3].text.strip()
            odd = cols[4].text.strip()

            if time.lower() != "time":
                predictions.append(
                    f"🕓 Time : {time}\n🏆 League : {league}\n⚔️ Match : {match}\n🎯 Tip : {tip}\n💸 Odd : {odd}"
                )

    if not predictions:
        return "😴 تم الانتهاء من جميع مباريات اليوم\n📅 توقعات الغد ستكون متوفرة قريباً، لا تنسَ العودة لاحقاً!"

    return "⚽️ مباريات اليوم:\n\n" + "\n\n".join(predictions)

# تحقق من الاشتراك
async def is_user_subscribed(context, user_id):
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# أمر start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = datetime.datetime.now().strftime("%A")  # اليوم فقط
    keyboard = [[InlineKeyboardButton("✅ نعم", callback_data="yes_first")]]
    await update.message.reply_text(
        f"👋🏻 مرحباً بك صديقي!\n\n✅ واش بغيتي توقعات يوم {day}؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# التفاعل مع الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "yes_first":
        is_sub = await is_user_subscribed(context, query.from_user.id)
        if is_sub:
            predictions = get_predictions()
            await query.message.reply_text(predictions)
        else:
            keyboard = [
                [InlineKeyboardButton("📢 إشترك في القناة", url="https://t.me/zri9abet")],
                [InlineKeyboardButton("✅ نعم، إشتركت", callback_data="confirm_sub")]
            ]
            await query.message.reply_text(
                "❌ إشترك في قناة البوت أولاً 👇🏻\nhttps://t.me/zri9abet\n\nإذا اشتركت في القناة إضغط نعم ✅",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    elif query.data == "confirm_sub":
        is_sub = await is_user_subscribed(context, query.from_user.id)
        if is_sub:
            predictions = get_predictions()
            await query.message.reply_text(predictions)
        else:
            await query.message.reply_text("❌ مزال ما إشتركتش، جرب من جديد من بعد ما تشترك.")

# إطلاق البوت
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
print("✅ Bot is running...")
app.run_polling()
