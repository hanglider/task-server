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
    #self.slave_hosts = ['192.168.1.107:5001']
    from tasks.task_manager import task_manager
    slave_urls = task_manager.slave_hosts
    
    heartbeat = Heartbeat(node_type='main', slave_urls=slave_urls)
    await heartbeat.start()

def main():
    host = os.getenv("HOST", "192.168.1.107")
    port = int(os.getenv("PORT", 5000))

    print(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
    asyncio.run(start_heartbeat())

if __name__ == "__main__":
    main()