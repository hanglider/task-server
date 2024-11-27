from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tasks.task_manager import task_manager
from tasks.task_processing import distribute_files_to_slaves
import asyncio

router = APIRouter()


class TaskResult(BaseModel):
    task_id: str
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
    print(f"Task {task_result.task_id} completed by slave {task_result.slave_ip} with result: {task_result.result}")

    if not task_result.result:
        raise HTTPException(status_code=400, detail="Result cannot be empty")
    if not task_result.slave_ip:
        raise HTTPException(status_code=400, detail="Slave IP cannot be empty")

    task_manager.available_hosts.append(task_result.slave_ip)

    if task_manager.available_hosts:
        asyncio.create_task(distribute_files_to_slaves())

    return {"message": f"Task {task_result.task_id} from {task_result.slave_ip} successfully received", "status": "success"}