from fastapi import APIRouter, UploadFile, File, HTTPException
from tasks.task_manager import task_manager
from utils.file_utils import main_save_uploaded_files
from tasks.task_processing import distribute_files_to_slaves
import asyncio
import os
from typing import List
import importlib
import aiofiles
from pathlib import Path

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

@router.post("/main_upload_files")
async def upload(files: List[UploadFile] = File(...)):
    os.makedirs("app/incoming", exist_ok=True)
    filenames = await main_save_uploaded_files(files, "incoming", task_manager.main_file_index)

    for filename in filenames:
        if 'task' in filename:
            module_name = os.path.basename(filename.split(".")[0])
            task_module = importlib.import_module(f'incoming.{module_name}')
            task_module.cut_jpg(f"app/incoming/data{task_manager.main_file_index}.jpg", r"", task_manager.main_file_index)
            folder_path = Path('app/incoming')
            for file in folder_path.iterdir():
                if 'part' in file.name:
                    if str(task_manager.main_file_index) in file.name.split("!")[1][0]:
                        task_manager.add_file_to_queue(f"app/incoming/{file.name}", filename)           
    if task_manager.available_hosts:
        asyncio.create_task(distribute_files_to_slaves())
    task_manager.main_file_index += 1
    return {"message": f"Successfully uploaded files: {filenames}"}
