import asyncio
import asyncio
from fastapi import FastAPI
from starlette.responses import JSONResponse
from bot import run_bot

app = FastAPI()

bot_task = None


@app.get("/")
async def home():
    return JSONResponse({"status": "ok"})


@app.on_event("startup")
async def start_bot():
    global bot_task

    # если бот уже работает — не запускаем второй
    if bot_task is None or bot_task.done():
        bot_task = asyncio.create_task(run_bot())


@app.on_event("shutdown")
async def stop_bot():
    global bot_task

    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass