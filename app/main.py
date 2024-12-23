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
from utils import network_utils

label = ""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация при запуске приложения
    print("Инициализация приложения...")
    asyncio.create_task(start_task_manager())
    
    print("Приложение готово к работе")
    yield
    print("Завершение приложения...")

async def scan_for_slaves():
    while True:
        await asyncio.sleep(1)
        data = await asyncio.create_task(network_utils.get_ips(main_routes.HOSTS_DB))
        
        slave_ips = [ip for ip, info in data.items() if info.get("label") == 'slave']
        
        if slave_ips:
            return slave_ips

async def start_task_manager():
    if label == "main":
        db_ip = ""
        while True:
            await asyncio.sleep(1)
            data = await asyncio.create_task(network_utils.get_ips(main_routes.HOSTS_DB))
            for ip, info in data.items():
                if info.get("label") == 'db':
                    db_ip = ip
            if db_ip != "":
                break
        print("start")
        while True:
            await asyncio.sleep(1)
            slave_ips = await scan_for_slaves()
            task_manager.available_hosts = list(set(task_manager.available_hosts) | set(slave_ips))
            await main_routes.download_and_process_files(task_manager, db_ip)
            await main_routes.distribute_files_to_slaves(task_manager)

app = FastAPI(lifespan=lifespan)

app.include_router(main_routes.router)
app.include_router(slave_routes.router)
app.include_router(result_routes.router)

if __name__ == "__main__":
    name = socket.gethostname()
    host = socket.gethostbyname(name)
    port = 5000
    main_routes.set_port(port, host)
    result = network_utils.send_ip_to_server(host, port)
    label = result['label']
    uvicorn.run(app, host=host, port=port)
