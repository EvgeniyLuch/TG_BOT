import os
print("TG_TOKEN =", repr(os.getenv("TG_TOKEN")))
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


@dp.message(Command("start"))
async def start(message: types.Message):
    subscribed_users.add(message.chat.id)
    await message.answer("Ты подписался на ежедневные уведомления! Чтобы выключить — напиши /stop.")


@dp.message(Command("stop"))
async def stop(message: types.Message):
    subscribed_users.discard(message.chat.id)
    await message.answer("Уведомления выключены.")


async def daily_notifications():
    """Отправляет уведомления всем подписавшимся пользователям раз в день."""
    while True:
        now = datetime.datetime.now()
        today = now.date()

        if is_study_day(today):
            text = "📚 Ещё минус один учебный день!"
        elif is_weekend(today):
            text = "😎 Сегодня выходной!"
        elif is_winter_break(today):
            text = "❄️ Зимние каникулы! Учёбы нет!"
        elif is_summer_break(today):
            text = "☀️ Летние каникулы!"
        elif is_holiday(today):
            text = "🎉 Праздник! Учёбы нет!"
        else:
            text = "Сегодня нет учёбы!"

        for user_id in subscribed_users:
            try:
                await bot.send_message(user_id, text)
            except:
                pass

        # ждем до следующего дня
        await asyncio.sleep(86400)


async def run_bot():
    asyncio.create_task(daily_notifications())
    await dp.start_polling(bot)

