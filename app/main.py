import os
import uvicorn
from fastapi import FastAPI
from routes import main_routes, slave_routes, result_routes
from utils.network_utils import send_heartbeat
import socket

app = FastAPI()

# Подключение маршрутов
app.include_router(main_routes.router)
app.include_router(slave_routes.router)
app.include_router(result_routes.router)

# async def start_server():
#     name = socket.gethostname()
#     host = socket.gethostbyname(name)

#     print(f"Starting server on {host}:{5000}")
#     config = uvicorn.Config(app, host=host, port=5000)
#     server = uvicorn.Server(config)
#     await main_routes.start()
#     await server.serve()

if __name__ == "__main__":
    # Запуск приложения с помощью uvicorn
    main_routes.set_port(5000)
    uvicorn.run(app, host="192.168.1.107", port=5000)