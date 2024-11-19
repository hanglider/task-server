from application import app
from application.routes import main_routes, slave_routes, result_routes

# Подключение маршрутов
app.include_router(main_routes.router)
app.include_router(slave_routes.router)
app.include_router(result_routes.router)

# Запуск: uvicorn app.main:app --reload