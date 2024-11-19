import asyncio
import aiohttp
from app.tasks.task_manager import task_manager


async def distribute_files_to_slaves(url: str):
    print("Sending files to slaves")
    if not task_manager.queue["tasks"] or not task_manager.queue["datas"]:
        return

    task_file = task_manager.queue["tasks"].pop(0)
    data_file = task_manager.queue["datas"].pop(0)

    form_data = aiohttp.FormData()
    form_data.add_field('files', open(task_file, 'rb'), filename=task_file, content_type='application/octet-stream')
    form_data.add_field('files', open(data_file, 'rb'), filename=data_file, content_type='application/octet-stream')

    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://{url}/slave_upload_files", data=form_data) as response:
            print(await response.json())


async def process_task():
    await asyncio.sleep(5)
    print("Task processed")
