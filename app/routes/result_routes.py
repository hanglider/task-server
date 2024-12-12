from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tasks.task_manager import task_manager
from tasks.task_processing import distribute_files_to_slaves
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
    """
    print("[from result_route.py] task_completed")
    is_filled, index = task_manager.add_result_to_list(task_result.meta_data, task_result.result)
    if is_filled:
        print(f"\033[34mTask with index {index} has been fully completed!\033[0m")
        os.makedirs('app/results/', exist_ok=True)
        async with aiofiles.open(f"app/results/result{index}.txt", 'w') as f:
            await f.write(str(task_manager.results[index]))

    if not task_result.result:
        raise HTTPException(status_code=400, detail="Result cannot be empty")
    if not task_result.slave_ip:
        raise HTTPException(status_code=400, detail="Slave IP cannot be empty")

    print("[from result_route.py] appending hosts to available_hosts")
    task_manager.available_hosts.append(task_result.slave_ip)

    return {"message": f"Task {task_result.meta_data} from {task_result.slave_ip} successfully received", "status": "success"}