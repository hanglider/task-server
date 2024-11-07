import asyncio
import aiohttp
import time

async def send_files(url, task, data, index):
    form_data = aiohttp.FormData()
    form_data.add_field('files', task, filename=f'task{index}.py', content_type='application/octet-stream')
    form_data.add_field('files', data, filename=f'data{index}.jpg', content_type='application/octet-stream')

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=form_data) as response:
            return await response.json()

async def main():
    task_path = str(input('Введите путь к исполняемому файлу: '))
    data_path = str(input('Введите путь к файлу c данными: '))

    with open(task_path, 'rb') as task_file, open(data_path, 'rb') as data_file:
        task = task_file.read()
        data = data_file.read()

        urls = [
            'http://192.168.1.107:5000/main_upload_files',
            'http://192.168.1.107:5000/main_upload_files',
            'http://192.168.1.107:5000/main_upload_files',
        ]

        start_time = time.time()
        
        tasks = []
        for i in range(len(urls)):
            tasks.append(send_files(urls[i], task, data, i))
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        print('Elapsed time: ', elapsed_time)
        
        for result in results:
            print(result)

asyncio.run(main())

# Z:\Korhov\task-server\mytask.py
# Z:\Korhov\task-server\test_negr.jpg