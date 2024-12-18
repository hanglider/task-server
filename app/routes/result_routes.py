from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from tasks.task_manager import task_manager
from tasks.task_processing import distribute_files_to_slaves
import asyncio
import aiofiles
import os
import httpx
import aiohttp


router = APIRouter()

DB_IP = "172.20.10.7:8000"

class TaskResult(BaseModel):
    meta_data: str
    result: str
    slave_ip: str


@router.post('/task_completed')
async def task_completed(task_result: TaskResult):
    """
    Endpoint to receive notifications from slave nodes when a task is completed.
    """
    if not task_result.result:
        raise HTTPException(status_code=400, detail="Result cannot be empty")
    if not task_result.slave_ip:
        raise HTTPException(status_code=400, detail="Slave IP cannot be empty")
    print("[from result_route.py] task_completed")
    print("[from result_route.py] appending hosts to available_hosts")

    task_manager.available_hosts.append(task_result.slave_ip)
    is_filled, index = task_manager.add_result_to_list(task_result.meta_data, task_result.result)
    if is_filled:
        print(f"\033[34mTask with index {index} has been fully completed!\033[0m")

        # return RedirectResponse(f"http://{DB_IP}/send_results")
        async with aiohttp.ClientSession() as session:
            payload = {
                "task_id": str(index),
                "task_result": str(task_manager.results[index]),
            }
            async with session.post(f"http://{DB_IP}/send_results", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to notify server: {response.status}"}
    
        # async with aiofiles.open(f"app/results/result{index}.txt", 'w') as f:
        #     await f.write(str(task_manager.results[index]))

        # form_data = aiohttp.FormData()
        # form_data.add_field('task_id', str(index))
        # form_data.add_field('task_result', str(task_manager.results[index]))

        # async with aiohttp.ClientSession() as session:
        #     async with session.post(f"http://{DB_IP}/send_results", data=form_data) as response:
        #         return await response.json()

        # async with aiohttp.ClientSession() as session:
        #     print(os.listdir("app/results"))
        # # Читаем содержимое файла в байтовом формате
        #     async with aiofiles.open(f"app/results/result{index}.txt", 'rb') as file:
        #         file_content = await file.read()  # Считываем содержимое файла
                
        #         # Формируем данные для отправки
        #         form_data = aiohttp.FormData()
        #         form_data.add_field("task_id", str(index))  # ID задачи как параметр
        #         form_data.add_field(
        #         "task_result",
        #         file_content,  # Содержимое файла
        #         filename=f"result{index}.txt",  # Имя файла
        #         content_type="application/octet-stream"  # MIME-тип
        #         )
                
        #         # Выполняем запрос
        #         try:
        #             async with session.post(f"http://{DB_IP}/send_results", data=form_data) as response:
        #                 # Обработка ответа
        #                 print("Status Code:", response.status)
        #                 try:
        #                     result = await response.json()  # Парсим JSON
        #                     print("Response JSON:", result)
        #                 except Exception as e:
        #                     print(f"Failed to parse JSON: {e}")
        #         except aiohttp.ClientError as e:
        #             print(f"Request failed: {e}")

    else:
        return {"message": f"Task {task_result.meta_data} from {task_result.slave_ip} successfully received", "status": "success"}