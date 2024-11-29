from fastapi import APIRouter, UploadFile, File, HTTPException
from monitoring.heartbeat2 import Heartbeat
from utils.file_utils import main_save_uploaded_files, slave_save_uploaded_files
from tasks.task_processing import process_task
import asyncio
import os
from typing import List

router = APIRouter()

# Heartbeat для уведомления основного сервера
async def start_slave_heartbeat():
    """
    Отправка heartbeat основному серверу.
    """
    main_server_url = "http://192.168.1.107:5000"
    heartbeat = Heartbeat(node_type='slave', main_server_url=main_server_url)
    await heartbeat.start()

@router.on_event("startup")
async def startup_event():
    """
    Запускает heartbeat при старте узла.
    """
    asyncio.create_task(start_slave_heartbeat())

@router.get("/heartbeat")
async def heartbeat():
    """
    Эндпоинт для приема heartbeat-запросов.
    """
    return {"status": "alive"}

@router.post('/slave_upload_files')
async def slave_upload(files: List[UploadFile] = File(...)):
    os.makedirs("app/test_incoming", exist_ok=True)
    filenames = await slave_save_uploaded_files(files, "test_incoming")


    asyncio.create_task(process_task("test_incoming"))

    return {"message": "Files successfully uploaded"}
