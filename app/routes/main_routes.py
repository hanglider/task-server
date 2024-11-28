from fastapi import APIRouter, UploadFile, File, HTTPException
from tasks.task_manager import task_manager
from utils.file_utils import main_save_uploaded_files
from tasks.task_processing import distribute_files_to_slaves
import asyncio
import os
from typing import List
import importlib
import aiofiles

router = APIRouter()


@router.post("/main_upload_files")
async def upload(files: List[UploadFile] = File(...)):
    os.makedirs("app/incoming", exist_ok=True)
    filenames = await main_save_uploaded_files(files, "incoming", task_manager.main_file_index)

    #TODO: запрос файлов из бд, их разрезание и добавление в очередь

    

    for filename in filenames:
        # Проверяем, если файл не в очереди
        if filename not in task_manager.queue['tasks'] and filename not in task_manager.queue['datas']:
            if 'task' in filename:
                module_name = filename[13:18]
                import incoming.task0
                task_module = importlib.import_module(f'incoming.{module_name}')
                task_module.cut_jpg(f"{filename[:13]}data{filename[17]}.jpg", r"", task_manager.main_file_index)
                
                folder_path = 'app/incoming'
                # Сохраняем список всех файлов, которые содержат 'image'
                image_files = [part_name for part_name in os.listdir(folder_path) 
                            if os.path.isfile(os.path.join(folder_path, part_name)) and 'image' in part_name]
                
                # Добавляем файл 'task' в очередь столько раз, сколько есть 'image'
                for _ in image_files:
                    task_manager.add_file_to_queue(filename)
                
                # Убираем дублирование файлов с 'image'
                for part_name in image_files:
                    task_manager.add_file_to_queue(f'app/incoming/{part_name}')

    print(task_manager.queue)                


    #TODO: смотри distribute_files_to_slaves
    if task_manager.available_hosts:
        asyncio.create_task(distribute_files_to_slaves())

    task_manager.main_file_index += 1
    return {"message": f"Successfully uploaded files: {filenames}"}
