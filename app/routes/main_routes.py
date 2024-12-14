import aiofiles
import aiohttp
from fastapi import APIRouter
from tasks.task_manager import task_manager
from utils.file_utils import extract_zip_with_index
from tasks.task_processing import distribute_files_to_slaves
import os
from typing import List
import importlib
from pathlib import Path
import httpx
from tasks.task_manager import TaskManager

HOSTS_DB = "172.20.10.7:8001"

router = APIRouter()
######
from pydantic import BaseModel

class HeartbeatRequest(BaseModel):
    slave_ip: str

@router.post('/heartbeat')
async def heartbeat(request: HeartbeatRequest):
    slave_ip = request.slave_ip
    if slave_ip not in task_manager.available_hosts:
        task_manager.available_hosts.append(slave_ip)
    return {"message": "Heartbeat received"}
######

processed_files = set()  # Хранение обработанных файлов

async def download_and_process_files(task_manager: TaskManager, db_ip):
    if len(task_manager.available_hosts) == 0:
        pass
    os.makedirs("app/incoming", exist_ok=True)

    try:
        # Загрузка ZIP-файла
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{db_ip}/download")
        if response.status_code != 200:
            raise Exception(f"Failed to download file: {response.status_code}")

        zip_path = "app/incoming/temp.zip"
        with open(zip_path, "wb") as f:
            f.write(response.content)
        
        # TODO в этом месте ты должен вытащить id записи в бд из респонса
        # task_manager.main_file_index заменить на id

        id = response.headers.get("X-Task-ID")

        await extract_zip_with_index(zip_path, "app/incoming", id)
        os.remove(zip_path)

        # Обработка файлов
        filenames = os.listdir("app/incoming")
        for filename in filenames:
            if 'task' in filename and filename not in processed_files:  # Проверка на уже обработанный файл
                processed_files.add(filename)  # Отмечаем файл как обработанный
                module_name = filename.split(".")[0]
                task_module = importlib.import_module(f'incoming.{module_name}')
                data_filepath = f"app/incoming/data{id}.jpg"
                task_module.cut_jpg(data_filepath, r"", id)

                # Добавление частей в очередь
                folder_path = Path('app/incoming')
                for file in folder_path.iterdir():
                    if 'part' in file.name and str(id) in file.name.split("!")[1][0]:
                        task_manager.add_file_to_queue(str(file), f"app/incoming/{filename}")
    except Exception as e:
        print(f"Error processing files: {e}")


async def distribute_files_to_slaves(task_manager):
    if len(task_manager.available_hosts) == 0:
        pass
    print(task_manager.available_hosts)
    while task_manager.queue and task_manager.available_hosts:
        data_file, task_file = task_manager.queue.pop(0)
        host = task_manager.available_hosts.pop(0)

        try:
            async with aiohttp.ClientSession() as session:
                async with aiofiles.open(data_file, "rb") as data_f, aiofiles.open(task_file, "rb") as task_f:
                    form_data = aiohttp.FormData()
                    form_data.add_field('files', data_f, filename=os.path.basename(data_file))
                    form_data.add_field('files', task_f, filename=os.path.basename(task_file))

                    async with session.post(f"http://{host}/slave_upload_files", data=form_data) as response:
                        if response.status == 200:
                            print(f"Task ({data_file},{task_file}) sent to {host}")
                        else:
                            print(f"Failed to send task to {host}: {response.status}")
        except Exception as e:
            print(f"Error sending to {host}: {e}")
        finally:
            task_manager.available_hosts.append(host)

g_port = 0
g_host = 0

def set_port(port, host):
    global g_port
    g_port = port
    global g_host
    g_host = host

