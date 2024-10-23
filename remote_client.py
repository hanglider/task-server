import asyncio
import aiohttp
import time

main_host = '192.168.1.107'

async def main(server_ip):
    task_path = str(input('Введите путь к исполняемому файлу: '))
    data_path = str(input('Введите путь к файлу c данными: '))
    url = f'http://{main_host}:5000/main_upload_files'
    with open(task_path, 'rb') as upl_task:
        task = upl_task
        with open(data_path, 'rb') as upl_data:
            data = upl_data
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={'data' : data, 'task' : task}) as response:
                    return await response.read()
      
asyncio.run(main(main_host))
print(f'отправлено на {main_host}')



