from fastapi import APIRouter, UploadFile, File, HTTPException
from tasks.task_manager import task_manager
from utils.file_utils import extract_zip_with_index
from tasks.task_processing import distribute_files_to_slaves
import asyncio
import os
from typing import List
import importlib
import aiofiles
from pathlib import Path
import httpx
import zipfile
import socket

DB_IP = "192.168.1.107:8000"

router = APIRouter()
######
from pydantic import BaseModel
from tasks.task_manager import task_manager

class HeartbeatRequest(BaseModel):
    slave_ip: str

@router.post('/heartbeat')
async def heartbeat(request: HeartbeatRequest):
    slave_ip = request.slave_ip
    if slave_ip not in task_manager.available_hosts:
        task_manager.available_hosts.append(slave_ip)
    return {"message": "Heartbeat received"}
######

async def manage_tasks():
    os.makedirs("app/incoming", exist_ok=True)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{DB_IP}/download")

        if response.status_code != 200:
            print(f"Error downloading file: {response.status_code}")
            print(response.text)  # Вывод текста ошибки для диагностики
            raise Exception("Failed to download file")

        # Путь для сохранения ZIP-файла
        zip_path = "app/incoming/temp.zip"
        with open(zip_path, "wb") as zip_file:
            zip_file.write(response.content)

        await extract_zip_with_index("app/incoming/temp.zip", "app/incoming", task_manager.main_file_index)

        os.remove(zip_path)

        filenames = os.listdir("app/incoming")

        for filename in filenames:
            if 'task' in filename:
                module_name = os.path.basename(filename.split(".")[0])
                task_module = importlib.import_module(f'incoming.{module_name}')
                filepath = f"app/incoming/data{task_manager.main_file_index}.jpg"
                task_module.cut_jpg(filepath, r"", task_manager.main_file_index)
                folder_path = Path('app/incoming')
                for file in folder_path.iterdir():
                    if 'part' in file.name:
                        if str(task_manager.main_file_index) in file.name.split("!")[1][0]:
                            task_manager.add_file_to_queue(f"app/incoming/{file.name}", f"app/incoming/{filename}")           
        if task_manager.available_hosts:
            asyncio.create_task(distribute_files_to_slaves())
        task_manager.main_file_index += 1
        if len(task_manager.queue) <= len(task_manager.available_hosts):
            asyncio.create_task(manage_tasks())

    except HTTPException as e:
        if e.status_code == 404:
            print(f"No files available for download. {e}")
        raise

g_port = 0

def set_port(port):
    global g_port
    g_port = port

@router.on_event("startup")
async def start():
    name = socket.gethostbyname(socket.gethostname())
    global g_port
    print(f"{name}:{g_port}")
    if f"{name}:{g_port}" not in task_manager.available_hosts:
        await manage_tasks()
