# main.py
import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from aiogram.types import Update
from bot import bot, dp, daily_notifications

app = FastAPI()

# WEBHOOK_URL должен быть вида: https://your-service.onrender.com
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if not WEBHOOK_URL:
    # для безопасности: если не задан, приложение всё равно стартует, но предупреждает
    print("Warning: WEBHOOK_URL env var not set. Set WEBHOOK_URL to your Render URL (without /webhook).")

full_webhook = (WEBHOOK_URL.rstrip("/") if WEBHOOK_URL else "") + "/webhook"

bg_task = None

@app.on_event("startup")
async def on_startup():
    # устанавливаем webhook только если есть WEBHOOK_URL
    if WEBHOOK_URL:
        await bot.set_webhook(full_webhook)
        print("Webhook set to:", full_webhook)
    else:
        print("WEBHOOK_URL not set — webhook not registered.")

    # запускаем фоновые уведомления (если ещё не запущены)
    global bg_task
    if bg_task is None or bg_task.done():
        bg_task = asyncio.create_task(daily_notifications())
        print("Started daily_notifications background task.")

@app.on_event("shutdown")
async def on_shutdown():
    # корректно удаляем webhook
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print("Error deleting webhook:", e)

    # останавливаем bg задачу
    global bg_task
    if bg_task:
        bg_task.cancel()
        try:
            await bg_task
        except asyncio.CancelledError:
            pass

@app.post("/webhook")
async def telegram_webhook(request: Request):
    if not WEBHOOK_URL:
        # не должно принимать апдейты, если WEBHOOK_URL не настроен
        raise HTTPException(status_code=404, detail="Webhook not configured.")
    data = await request.json()
    update = Update.model_validate(data)
    # feed_update безопасен: передаём обновление в диспетчер aiogram
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok"}
