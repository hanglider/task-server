import asyncio
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from routes import main_routes, slave_routes, result_routes
from utils.network_utils import send_heartbeat
import socket
from fastapi import FastAPI
import uvicorn
import socket
from tasks.task_manager import task_manager

DB_IP = "192.168.1.107:8000"
NAME = socket.gethostname()
HOST = socket.gethostbyname(NAME)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация при запуске приложения
    print("Инициализация приложения...")
    asyncio.create_task(start_task_manager())

    # TODO: отправление своего ip в бд
    
    print("Приложение готово к работе")
    yield
    print("Завершение приложения...")


async def start_task_manager():
    if f"{HOST}:5000" not in task_manager.available_hosts:
        while True:
            await asyncio.sleep(1)  # Интервал для запуска задач
            await main_routes.download_and_process_files(task_manager, DB_IP)
            await main_routes.distribute_files_to_slaves(task_manager)


app = FastAPI(lifespan=lifespan)

# Подключение маршрутов
app.include_router(main_routes.router)
app.include_router(slave_routes.router)
app.include_router(result_routes.router)

if __name__ == "__main__":
    main_routes.set_port(5000)
    print(f"Запуск сервера на {HOST}:5000")
    uvicorn.run(app, host=HOST, port=5000)
