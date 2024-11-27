from fastapi import APIRouter, UploadFile, File, HTTPException
from tasks.task_manager import task_manager
from utils.file_utils import main_save_uploaded_files
from tasks.task_processing import distribute_files_to_slaves
import asyncio
import os
from typing import List

router = APIRouter()


@router.post("/main_upload_files")
async def upload(files: List[UploadFile] = File(...)):
    os.makedirs("app/incoming", exist_ok=True)
    filenames = await main_save_uploaded_files(files, "incoming", task_manager.main_file_index)

    #TODO: разрезание файлов, отправка разрезанных файлов на бд и добавление ссылок на эти куски в очередь

    for filename in filenames:
        task_manager.add_file_to_queue(filename)

    #TODO: смотри distribute_files_to_slaves
    if task_manager.available_hosts:
        asyncio.create_task(distribute_files_to_slaves())

    task_manager.main_file_index += 1
    return {"message": f"Successfully uploaded files: {filenames}"}
