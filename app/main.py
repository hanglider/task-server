from routes import main_routes, slave_routes, result_routes
from monitoring.heartbeat2 import Heartbeat
import os
import uvicorn
import asyncio
from fastapi import FastAPI

app = FastAPI()

# Подключение маршрутов
app.include_router(main_routes.router)
app.include_router(slave_routes.router)
app.include_router(result_routes.router)

async def start_heartbeat():
    """
    Запускает heartbeat для проверки узлов slave.
    """
    slave_urls = [
        'http://192.168.1.101:5001', 
        'http://192.168.1.102:5001'
        ]  # Адреса slave-узлов
    
    heartbeat = Heartbeat(node_type='main', slave_urls=slave_urls)
    await heartbeat.start()

def main():
    host = os.getenv("HOST", "192.168.1.107")
    port = int(os.getenv("PORT", 5000))

    print(f"Starting server on {host}:{port}")
    asyncio.create_task(start_heartbeat())
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()