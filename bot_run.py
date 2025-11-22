import asyncio
import time
from bot import run_bot  # твоя функция run_bot()

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(run_bot())
        except Exception as e:
            print("Bot crashed:", e)
            print("Restarting in 5 seconds...")
            time.sleep(5)
