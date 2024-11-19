from routes import main_routes, slave_routes, result_routes
import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

# Подключение маршрутов
app.include_router(main_routes.router)
app.include_router(slave_routes.router)
app.include_router(result_routes.router)

def main():
    host = os.getenv("HOST", "192.168.1.107")
    port = int(os.getenv("PORT", 5000))

    print(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()