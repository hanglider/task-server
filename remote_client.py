import asyncio
import aiohttp

hosts = ['192.168.1.102']

async def main(server_ip):
    task_path = str(input('Введите путь к исполняемому файлу: '))
    data_path = str(input('Введите путь к файлу c данными: '))
    url = f'http://{server_ip}:5000/upload_task'
    with open(task_path, 'rb') as upl_task:
        task = upl_task
        with open(data_path, 'rb') as upl_data:
            data = upl_data
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={'data' : data, 'task' : task}) as response:
                    return await response.read()

for host in hosts:          
    asyncio.run(main(host))
    print(f'отправлено на {host}')



