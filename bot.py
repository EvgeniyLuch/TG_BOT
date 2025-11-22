import datetime
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ==============================================
#              CONFIG
# ==============================================

API_TOKEN = os.getenv("TG_TOKEN")
END_DATE = datetime.date(2029, 5, 28)

# Праздники Узбекистана
UZ_HOLIDAYS = {
    (1, 1),
    (3, 8),
    (3, 21),
    (9, 1),
    (10, 1),
    (12, 8),
}

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Храним подписанных пользователей
subscribed_users = set()


# ==============================================
#              КАЛЕНДАРЬ / ЛОГИКА
# ==============================================

def is_holiday(date: datetime.date):
    return (date.month, date.day) in UZ_HOLIDAYS

def is_winter_break(date):
    return date.month == 1

def is_summer_break(date):
    return date.month in (6, 7, 8)

def is_end_of_year_break(date):
    return date.month == 12 and date.day >= 28

def is_weekend(date):
    return date.weekday() >= 5

def is_study_day(date):
    if is_weekend(date): return False
    if is_holiday(date): return False
    if is_winter_break(date): return False
    if is_summer_break(date): return False
    if is_end_of_year_break(date): return False
    return True


def count_total_days(today):
    return (END_DATE - today).days

def count_study_days(today):
    days = 0
    d = today
    while d <= END_DATE:
        if is_study_day(d):
            days += 1
        d += datetime.timedelta(days=1)
    return days


# ==============================================
#              ХЕНДЛЕРЫ
# ==============================================

@dp.message(Command("start"))
async def start(message: types.Message):
    subscribed_users.add(message.chat.id)
    await message.answer(
        "Зачем тебе это? Тебе делать нечего? Лучше выключить меня и не париться.\n"
        "Чтобы выключить — напиши /stop\n"
        "Статистика по дням — напиши /stat\n"
    )

@dp.message(Command("stop"))
async def stop(message: types.Message):
    subscribed_users.discard(message.chat.id)
    await message.answer("Уведомления выключены.")

@dp.message(Command("stat"))
async def stat(message: types.Message):
    today = datetime.datetime.now().date()

    remaining_days = count_total_days(today)
    remaining_study_days = count_study_days(today)

    # определяем статус сегодняшнего дня
    if is_study_day(today):
        base = "Сегодня учебный день."
    elif is_weekend(today):
        base = "Сегодня выходной."
    elif is_winter_break(today):
        base = "Сейчас зимние каникулы."
    elif is_summer_break(today):
        base = "Сейчас летние каникулы."
    elif is_holiday(today):
        base = "Сегодня праздник."
    else:
        base = "Сегодня учёбы нет."

    text = (
        f"{base}\n\n"
        f"📅 Осталось дней: {remaining_days}\n"
        f"📘 Осталось учебных дней: {remaining_study_days}"
    )

    await message.answer(text)


# ==============================================
#              ЕЖЕДНЕВНЫЕ ОПОВЕЩЕНИЯ
# ==============================================

async def daily_notifications():
    while True:
        today = datetime.datetime.now().date()

        # подсчёт
        remaining_days = count_total_days(today)
        remaining_study_days = count_study_days(today)

        # текст
        if is_study_day(today):
            base = "📚 Ещё минус один учебный день!"
        elif is_weekend(today):
            base = "😎 Сегодня выходной, хорошенько отдохни!"
        elif is_winter_break(today):
            base = "❄️ Зимние каникулы! Учёбы нет!"
        elif is_summer_break(today):
            base = "☀️ Летние каникулы!"
        elif is_holiday(today):
            base = "🎉 Праздник! Учёбы нет!"
        else:
            base = "Сегодня нет учёбы!"

        text = (
            f"{base}\n\n"
            f"📅 Общее количество дней: {remaining_days} дней\n"
            f"📘 Только учебные дни: {remaining_study_days}"
        )

        # отправка всем
        for user_id in subscribed_users:
            try:
                await bot.send_message(user_id, text)
            except:
                pass

        await asyncio.sleep(86400)


# ==============================================
#              ЗАПУСК БОТА
# ==============================================

async def run_bot():
    # важно для Render (выключает webhook)
    await bot.delete_webhook(drop_pending_updates=True)

    # запускаем уведомления
    asyncio.create_task(daily_notifications())

    # запускаем polling

    await dp.start_polling(bot)
