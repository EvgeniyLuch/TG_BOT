import datetime
import asyncio
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

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

# ===============================
#   ХРАНЕНИЕ ПОДПИСЧИКОВ
# ===============================

USERS_FILE = "users.json"


def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def save_users():
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(subscribed_users), f)
    except Exception as e:
        print("Failed to save users:", e)


# Загружаем подписчиков при старте
subscribed_users = load_users()


# ===============================
#     ВРЕМЯ УЗБЕКИСТАНА
# ===============================

def uz_now():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=5)


def uz_today():
    return uz_now().date()


# ===============================
#     ЛОГИКА КАЛЕНДАРЯ
# ===============================

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


# ===============================
#          ХЕНДЛЕРЫ
# ===============================

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    subscribed_users.add(message.chat.id)
    save_users()

    await message.answer(
        "Ну и нахера тебе это? Просто считать дни, как заключенный - это вообще то странно.\n"
        "Чтобы выключить — напиши /stop.\n"
        "Статистика по дням — напиши /stat"
    )


@dp.message(Command("stop"))
async def stop_handler(message: types.Message):
    subscribed_users.discard(message.chat.id)
    save_users()

    await message.answer("Решение здорового человека!")


@dp.message(Command("stat"))
async def stat_handler(message: types.Message):
    today = uz_today()
    remaining_days = count_total_days(today)
    remaining_study_days = count_study_days(today)

    if is_study_day(today):
        base = "☠️🍒Сегодня учебный день(((("
    elif is_weekend(today):
        base = "🍀🕎Сегодня отдыхаем!!!"
    elif is_winter_break(today):
        base = "🏳️‍⚧️📈Сейчас зимние каникулы!!!"
    elif is_summer_break(today):
        base = "🌡️🍾Сейчас летние каникулы!!!"
    elif is_holiday(today):
        base = "🐢🤌Сегодня праздник!!!"
    else:
        base = "😈🌵Сегодня учёбы нет!!!"

    text = (
        f"{base}\n\n"
        f"📅 Осталось дней: {remaining_days}\n"
        f"📘 Осталось учебных дней: {remaining_study_days}"
    )
    await message.answer(text)


# ===============================
#     ЕЖЕДНЕВНЫЕ УВЕДОМЛЕНИЯ
# ===============================

async def daily_notifications():
    while True:
        now = uz_now()
        today = uz_today()

        # ТВОЁ ВРЕМЯ УВЕДОМЛЕНИЯ — УСТАНОВИ ЛЮБОЕ
        target = now.replace(hour=8, minute=30, second=0, microsecond=0)

        # Если бот был перезапущен ПОСЛЕ 09:05 — отправить сразу
        if now > target:
            print("Missed scheduled time — sending NOW")
            await send_daily_message(today)
            target += datetime.timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        print(f"Next notification in {wait_seconds/3600:.2f} hours (UZ time)")

        await asyncio.sleep(wait_seconds)

        # ВО ВРЕМЯ — отправляем
        today = uz_today()
        await send_daily_message(today)


async def send_daily_message(today):
    if is_study_day(today):
        base = "🇮🇱🍆 Ещё один блятский день учебы."
    elif is_weekend(today):
        base = " 🗽🚬Сегодня выходной, хорошенько отдохни!"
    elif is_winter_break(today):
        base = "💰🍻 Зимние каникулы! Нахуй учебу! "
    elif is_summer_break(today):
        base = " Летние каникулы! Забей на всё!"
    elif is_holiday(today):
        base = "🎃🥞 Праздник! Учёба идет нахер!"
    else:
        base = "⚔️🏴‍☠️Сегодня нет учёбы!"

    text = (
        f"{base}\n\n"
        f"📅 Общее количество дней: {count_total_days(today)} дней\n"
        f"📘 Только учебные дни: {count_study_days(today)}"
    )

    for user_id in list(subscribed_users):
        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")




