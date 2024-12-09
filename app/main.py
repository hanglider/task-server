import os
import uvicorn
from fastapi import FastAPI
from routes import main_routes, slave_routes, result_routes
from utils.network_utils import send_heartbeat
import asyncio

app = FastAPI()

# Подключение маршрутов
app.include_router(main_routes.router)
app.include_router(slave_routes.router)
app.include_router(result_routes.router)

async def start_server():
    host = os.getenv("HOST", "192.168.100.5")
    port = int(os.getenv("PORT", 5000))

    print(f"Starting server on {host}:{port}")
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    # Запуск heartbeat-задачи
    asyncio.create_task(send_heartbeat("http://192.168.100.5:5000/heartbeat"))
    await start_server()

if __name__ == "__main__":
    asyncio.run(main())
