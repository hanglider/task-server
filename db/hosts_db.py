import socket
from fastapi import FastAPI, Request, HTTPException
import json
from pathlib import Path

from pydantic import BaseModel

app = FastAPI()

# Путь к JSON-файлу
JSON_FILE = Path("client_ips.json")

# Проверяем, существует ли файл, если нет - создаем его
if not JSON_FILE.exists():
    with open(JSON_FILE, "w") as f:
        json.dump({}, f)

# Функция для загрузки данных из файла
def load_data():
    with open(JSON_FILE, "r") as f:
        return json.load(f)

# Функция для сохранения данных в файл
def save_data(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

class CLientIP(BaseModel):
    ip: str


@app.post("/add_ip")
async def add_ip(ip : CLientIP):
    # Получаем IP клиента
    # client_ip = request.client.host
    client_ip = ip.ip
    if not client_ip:
        raise HTTPException(status_code=400, detail="IP address not found")

    # Загружаем текущие данные
    data = load_data()

    # Проверяем, есть ли IP в данных
    if client_ip in data:
        return {"message": "IP already exists", "ip": client_ip, "label": label}

    # Определяем метку для IP
    label = "main" if len(data) == 0 else "slave"
    if len(data) == 0 or (list(data.values())[0]['label'] == 'db' and len(data) == 1):
        label = 'main'
    else:
        label = 'slave'
    label = "db" if client_ip.split(":")[1][0] == "8" else label

    # Добавляем новый IP как ключ с пустым списком и меткой
    data[client_ip] = {"logs": [], "label": label}
    save_data(data)

    return {"message": "IP added successfully", "ip": client_ip, "label": label}

@app.get("/get_ips")
async def get_ips():
    # Возвращаем текущие данные
    data = load_data()
    return {"ips": data}

@app.post("/add_log/{ip}")
async def add_log(ip: str, log: str):
    # Загружаем текущие данные
    data = load_data()

    # Проверяем, существует ли IP в данных
    if ip not in data:
        raise HTTPException(status_code=404, detail="IP address not found")

    # Добавляем лог в список логов указанного IP
    data[ip]["logs"].append(log)
    save_data(data)

    return {"message": "Log added successfully", "ip": ip, "log": log}

if __name__ == "__main__":
    import uvicorn
    name = socket.gethostname()
    host = socket.gethostbyname(name)
    uvicorn.run(app, host=host, port=8001)