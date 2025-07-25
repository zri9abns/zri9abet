import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)
import requests
from bs4 import BeautifulSoup
import datetime

TOKEN = "7522961870:AAEf9hvKs5gdPlN4q3Cub61v-BFFeyPVNDA"
CHANNEL_USERNAME = "zri9abet"  # بدون @

logging.basicConfig(level=logging.INFO)

LEAGUE_MAP = {
    "SWE": "Sweden 🇸🇪", "GER": "Germany 🇩🇪", "ENG": "England 🏴",
    "SPA": "Spain 🇪🇸", "ITA": "Italy 🇮🇹", "FRA": "France 🇫🇷",
    "NED": "Netherlands 🇳🇱", "POR": "Portugal 🇵🇹", "BEL": "Belgium 🇧🇪",
    "NOR": "Norway 🇳🇴", "DEN": "Denmark 🇩🇰", "FIN": "Finland 🇫🇮",
    "TUR": "Turkey 🇹🇷", "GRE": "Greece 🇬🇷", "MAR": "Morocco 🇲🇦",
    "KSA": "Saudi Arabia 🇸🇦", "EGY": "Egypt 🇪🇬", "ALG": "Algeria 🇩🇿",
    "TUN": "Tunisia 🇹🇳", "UAE": "UAE 🇦🇪", "QAT": "Qatar 🇶🇦",
    "USA": "USA 🇺🇸", "BRA": "Brazil 🇧🇷", "ARG": "Argentina 🇦🇷",
    "JPN": "Japan 🇯🇵", "CHN": "China 🇨🇳", "KOR": "Korea 🇰🇷",
    "SUI": "Switzerland 🇨🇭", "CZE": "Czech 🇨🇿", "POL": "Poland 🇵🇱",
    "SRB": "Serbia 🇷🇸", "CRO": "Croatia 🇭🇷", "IRL": "Ireland 🇮🇪",
    "LTU": "Lithuania 🇱🇹", "EST": "Estonia 🇪🇪", "KAZ": "Kazakhstan 🇰🇿",
    "AZE": "Azerbaijan 🇦🇿", "GIB": "Gibraltar 🇬🇮", "ISL": "Iceland 🇮🇸",
    "BUL": "Bulgaria 🇧🇬", "NIR": "N. Ireland 🇬🇧", "MDA": "Moldova 🇲🇩"
}

def get_predictions():
    url = "https://bankerpredict.com/5-odds"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("tr")[1:]

    predictions = ""
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 5:
            time = cells[0].text.strip()
            league = cells[1].text.strip().upper()
            match = cells[2].text.strip()
            tip = cells[3].text.strip()
            odd = cells[4].text.strip() or "?"

            league_full = LEAGUE_MAP.get(league, league)

            predictions += (
                f"🕓 Time : {time}\n"
                f"🏆 League : {league_full}\n"
                f"⚔️ Match : {match}\n"
                f"🎯 Tip : {tip}\n"
                f"💸 Odd: {odd}\n"
                f"━━━━━━━━━━━━━━\n"
            )
    return predictions or "❌ لم يتم العثور على توقعات اليوم."

async def is_user_subscribed(context, user_id):
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.datetime.now().strftime("%A, %d %B %Y")
    keyboard = [[InlineKeyboardButton("✅ نعم، أريد التوقعات", callback_data="yes_first")]]
    await update.message.reply_text(
        f"🙋🏻 مرحباً بك!\n\n✅ هل تريد توقعات اليوم؟\n📅 تاريخ اليوم: {today}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "yes_first":
        if await is_user_subscribed(context, query.from_user.id):
            predictions = get_predictions()
            await query.edit_message_text(f"✅ توقعات اليوم:\n\n{predictions}")
        else:
            keyboard = [
                [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME}")],
                [InlineKeyboardButton("✅ نعم، اشتركت", callback_data="confirm_sub")],
            ]
            await query.edit_message_text(
                f"❌ يجب الاشتراك في القناة:\nhttps://t.me/{CHANNEL_USERNAME}\n\n📌 اشترك أولا ثم اضغط نعم:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    elif query.data == "confirm_sub":
        if await is_user_subscribed(context, query.from_user.id):
            predictions = get_predictions()
            await query.edit_message_text(f"✅ توقعات اليوم:\n\n{predictions}")
        else:
            await query.edit_message_text("❌ ما زلت لم تشترك، حاول مرة أخرى بعد الاشتراك.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

print("🤖 Bot is running...")
app.run_polling()
