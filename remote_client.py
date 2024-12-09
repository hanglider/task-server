import asyncio
import aiohttp
import time
from app.utils.network_utils import send_heartbeat

async def send_files(url, task, data):
    form_data = aiohttp.FormData()
    form_data.add_field('files', task, filename=f'task.py', content_type='application/octet-stream')
    form_data.add_field('files', data, filename=f'data.jpg', content_type='application/octet-stream')

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=form_data) as response:
            return await response.json()

async def main():
    task_path = str(input('Введите путь к исполняемому файлу: '))
    data_path = str(input('Введите путь к файлу c данными: '))
    task_path = r"C:\IT\task-server\mytask.py"
    data_path = r"C:\IT\task-server\negr.jpg"
    space_path = r"C:\IT\task-server\lakhta.jpg"

    with open(task_path, 'rb') as task_file, open(data_path, 'rb') as data_file, open(space_path, 'rb') as data_space:
        task = task_file.read()
        data = data_file.read()
        space = data_space.read()

        urls = [
            'http://192.168.100.5:5000/main_upload_files',
            'http://192.168.100.5:5000/main_upload_files',
            'http://192.168.100.5:5000/main_upload_files',
        ]

        start_time = time.time()

        print(await send_files(urls[0], task, data))
        print(await send_files(urls[1], task, data))
        print(await send_files(urls[2], task, space))
        end_time = time.time()

        elapsed_time = end_time - start_time
        print('Elapsed time: ', elapsed_time)
        await send_heartbeat("192.168.100.5:5000/heartbeat")

if __name__ == "__main__":
    # Запуск heartbeat-задачи
    #asyncio.create_task(send_heartbeat("192.168.100.5:5000/heartbeat"))
    asyncio.run(main())