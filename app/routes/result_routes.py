from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tasks.task_manager import task_manager
from tasks.task_processing import distribute_files_to_slaves
from routes.main_routes import manage_tasks
import asyncio
import aiofiles
import os

router = APIRouter()


class TaskResult(BaseModel):
    meta_data: str
    result: str
    slave_ip: str

@router.post('/task_completed')
async def task_completed(task_result: TaskResult):
    """
    Endpoint to receive notifications from slave nodes when a task is completed.

    Args:
        task_result (TaskResult): Contains the task ID, result, and slave node IP.

    Returns:
        dict: A success message.
    """
    isFilled, index = task_manager.add_result_to_list(task_result.meta_data, task_result.result)
    if isFilled:
        print(f"\033[34mTask with index {index} has been fully completed!\033[0m")
        os.makedirs('app/results/', exist_ok=True)
        async with aiofiles.open(f"app/results/result{index}", 'w') as f:
            await f.write(str(task_manager.results[index]))


    if not task_result.result:
        raise HTTPException(status_code=400, detail="Result cannot be empty")
    if not task_result.slave_ip:
        raise HTTPException(status_code=400, detail="Slave IP cannot be empty")

    task_manager.available_hosts.append(task_result.slave_ip)
    if len(task_manager.queue) == 0:
        asyncio.create_task(manage_tasks())
    if task_manager.available_hosts:
        asyncio.create_task(distribute_files_to_slaves())

    return {"message": f"Task {task_result.meta_data} from {task_result.slave_ip} successfully received", "status": "success"}
