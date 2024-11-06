import asyncio
import aiohttp
import time as t

main_host = '192.168.1.107'

async def main(server_ip):
    task_path = str(input('Введите путь к исполняемому файлу: '))
    data_path = str(input('Введите путь к файлу c данными: '))
    task_path = r"Z:\Korhov\task-server\mytask.py"
    data_path = r"Z:\Korhov\archive (2).zip"
    url = f'http://{main_host}:5000/main_upload_files'
    with open(task_path, 'rb') as upl_task:
        task = upl_task
        with open(data_path, 'rb') as upl_data:
            data = upl_data
            print(t.time())
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={'data' : data, 'task' : task}) as response:
                    print("huy")
      
asyncio.run(main(main_host))
print(f'отправлено на {main_host}')


# Z:\Korhov\task-server\mytask.py
# Z:\Korhov\task-server\test_negr.jpg



