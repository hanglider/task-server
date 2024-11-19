from fastapi import APIRouter
from pydantic import BaseModel
from app.tasks.task_manager import task_manager
from app.tasks.task_processing import distribute_files_to_slaves
import asyncio

router = APIRouter()


class StringRequest(BaseModel):
    content: str


@router.post('/results')
async def receive_results(request: StringRequest):
    task_manager.available_hosts.append('192.168.1.107:5001')
    print(f"Received message: {request.content}")

    if task_manager.queue["tasks"] and task_manager.available_hosts:
        asyncio.create_task(distribute_files_to_slaves(task_manager.available_hosts.pop(0)))

    return {"response": "Results received"}
