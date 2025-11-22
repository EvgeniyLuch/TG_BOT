import datetime
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

API_TOKEN = os.getenv("TG_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Праздники Узбекистана (фиксированные)
UZ_HOLIDAYS = {
    (1, 1),   # Новый год
    (3, 8),   # 8 марта
    (3, 21),  # Навруз
    (9, 1),   # День независимости
    (10, 1),  # День учителей
    (12, 8),  # День Конституции
}

END_DATE = datetime.date(2029, 12, 28)

# Подписки пользователей
subscribed_users = set()

def is_holiday(date: datetime.date):
    return (date.month, date.day) in UZ_HOLIDAYS

def is_winter_break(date):
    return date.month == 1

def is_summer_break(date):
    return date.month in (7, 8)

def is_end_of_year_break(date):
    return (date.month == 12 and date.day >= 28)

def is_weekend(date):
    return date.weekday() >= 5

def is_study_day(date):
    if is_weekend(date): return False
    if is_holiday(date): return False
    if is_winter_break(date): return False
    if is_summer_break(date): return False
    if is_end_of_year_break(date): return False
    return True


# ================================
#   НОВЫЕ ФУНКЦИИ (только они!)
# ================================

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


@dp.message(Command("start"))
async def start(message: types.Message):
    subscribed_users.add(message.chat.id)
    await message.answer("Зачем тебе это? Тебе делать нечего? Лучше выключить меня и не париться. Чтобы выключить — напиши /stop.")


@dp.message(Command("stop"))
async def stop(message: types.Message):
    subscribed_users.discard(message.chat.id)
    await message.answer("Уведомления выключены.")


async def daily_notifications():
    """Отправляет уведомления всем подписавшимся пользователям раз в день."""
    while True:
        now = datetime.datetime.now()
        today = now.date()

        # счётчики
        remaining_days = count_total_days(today)
        remaining_study_days = count_study_days(today)

        # основной текст
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

        # добавление данных
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

        # ждем до следующего дня
        await asyncio.sleep(86400)


async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(daily_notifications())
    await dp.start_polling(bot)

