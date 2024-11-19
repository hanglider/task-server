from fastapi import APIRouter, UploadFile, File, HTTPException
from tasks.task_manager import task_manager
from utils.file_utils import save_uploaded_files
from tasks.task_processing import distribute_files_to_slaves
import asyncio
import os
from typing import List

router = APIRouter()


@router.post("/main_upload_files")
async def upload(files: List[UploadFile] = File(...)):
    os.makedirs("incoming", exist_ok=True)
    filenames = await save_uploaded_files(files, "incoming", task_manager.main_file_index)

    for filename in filenames:
        task_manager.add_file_to_queue(filename)

    if task_manager.available_hosts:
        asyncio.create_task(distribute_files_to_slaves(task_manager.available_hosts.pop(0)))

    task_manager.main_file_index += 1
    return {"message": f"Successfully uploaded files: {filenames}"}
