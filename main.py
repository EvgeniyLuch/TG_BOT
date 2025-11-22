import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from bot import run_bot

app = FastAPI()

@app.get("/")
async def home():
    return JSONResponse({"status": "ok"})

@app.on_event("startup")
async def start_bot():
    # запускаем бота в фоне
    app.state.bot_task = asyncio.create_task(run_bot())

@app.on_event("shutdown")
async def stop_bot():
    # при остановке — корректно тушим polling
    task = getattr(app.state, "bot_task", None)
    if task:
        task.cancel()
        try:
            await task
        except:
            pass
