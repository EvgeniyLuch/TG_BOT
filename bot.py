import datetime
from telegram.ext import ApplicationBuilder, ContextTypes
from telegram.ext import JobQueue

TOKEN = "8508235166:AAE63_gkhzlHjT8VRMdAm97A1n9UVgVgYMU"   # ← сюда вставь свой токен
CHAT_ID = 586577316           # ← сюда вставь свой chat_id

# ==== Праздники Узбекистана ====
UZ_HOLIDAYS = {
    (1, 1), (1, 14),
    (3, 8), (3, 21),
    (5, 9),
    (9, 1),
    (10, 1),
    (12, 8),
}

def is_winter(date):
    return date.month == 1  # весь январь

def is_summer(date):
    return date.month in (6,7,8) or (date.month == 9 and date.day < 8)

def is_autumn(date):
    return (date.month == 9 and date.day >= 8) or date.month in (10,11) or (date.month == 12 and date.day <= 28)

def is_spring(date):
    return date.month in (2,3,4,5)

def is_weekend(date):
    return date.weekday() >= 5

def is_holiday(date):
    return (date.month, date.day) in UZ_HOLIDAYS

def is_study_day(date):
    if is_winter(date) or is_summer(date):
        return False
    if is_weekend(date):
        return False
    if is_holiday(date):
        return False
    return is_autumn(date) or is_spring(date)

def get_daily_message():
    today = datetime.date.today()

    if is_holiday(today):
        return "🎉 Сегодня праздник! Учёбы нет!"
    if is_winter(today) or is_summer(today):
        return "😎 Каникулы!"
    if is_weekend(today):
        return "Сегодня выходной! ✨"
    if is_study_day(today):
        return "Ещё минус один день учёбы! 📚💪"
    return "Сегодня учёбы нет."

async def daily_notify(context: ContextTypes.DEFAULT_TYPE):
    msg = get_daily_message()
    await context.bot.send_message(chat_id=CHAT_ID, text=msg)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    job_queue = app.job_queue

    # каждый день в 08:00
    job_queue.run_daily(daily_notify, time=datetime.time(hour=8, minute=0))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
