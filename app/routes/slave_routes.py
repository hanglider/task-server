from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.file_utils import slave_save_uploaded_files
from tasks.task_processing import process_task
import asyncio
import os
from typing import List
from log import log_action

router = APIRouter()

@router.post('/heartbeat')
async def heartbeat():
    log_action("Получен heartbeat от slave.")
    return {"message": "Heartbeat received"}

@router.post('/slave_upload_files')
async def slave_upload(files: List[UploadFile] = File(...)):
    """
    Обрабатывает загрузку файлов от slave.
    """
    try:
        os.makedirs("app/test_incoming", exist_ok=True)

        filenames, meta_data = await slave_save_uploaded_files(files, "test_incoming")
        log_action(f"Slave загрузил файлы: {', '.join(filenames)}")

        asyncio.create_task(process_task("test_incoming", meta_data))
        log_action("Асинхронная задача обработки файлов запущена.")

        return {"message": "Files successfully uploaded"}
    
    except Exception as e:
        log_action(f"Ошибка при загрузке файлов от slave: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при загрузке файлов.")