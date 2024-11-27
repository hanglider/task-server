import asyncio
import aiohttp
import time

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
    task_path = r"Z:\Korhov\task-server\mytask.py"
    data_path = r"Z:\Korhov\task-server\test_negr.jpg"
    space_path = r"Z:\Korhov\task-server\test_space.jpg"

    with open(task_path, 'rb') as task_file, open(data_path, 'rb') as data_file, open(space_path, 'rb') as data_space:
        task = task_file.read()
        data = data_file.read()
        space = data_space.read()

        urls = [
            'http://192.168.1.107:5000/main_upload_files',
            'http://192.168.1.107:5000/main_upload_files',
            'http://192.168.1.107:5000/main_upload_files',
        ]

        start_time = time.time()
        
        # tasks = []
        # for i in range(len(urls)):
        #     tasks.append(send_files(urls[i], task, data))
        
        # results = await asyncio.gather(*tasks)
        print(await send_files(urls[0], task, data))
        print(await send_files(urls[1], task, data))
        print(await send_files(urls[2], task, space))
        end_time = time.time()

        elapsed_time = end_time - start_time
        print('Elapsed time: ', elapsed_time)
        
        # for result in results:
        #     print(result)

asyncio.run(main())

# Z:\Korhov\task-server\mytask.py
# Z:\Korhov\task-server\test_negr.jpg