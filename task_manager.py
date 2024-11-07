import os
import asyncio
import aiohttp
from file_manager import save_file, merge_results
from taskprocessor import TaskProcessor

class TaskManager:
    def __init__(self):
        self.slave_hosts = ['192.168.1.107:5001']
        self.num_splits = 1

    async def process_task(self, index_part):
        from incomming import mytask
        task_processor = TaskProcessor(timeout=10)
        task_processor.add_task(mytask.main, mytask.load_image("test_incomming/data.jpg", self.num_splits)[index_part])
        results = await task_processor.run_all_tasks()
        await self.send_results('192.168.1.107:5000', results)

    async def handle_main_file_upload(self, files):
        os.makedirs("incomming", exist_ok=True)
        print(f"{t.time()}")
        save_file(files['data'], f'incomming/data.{files['data'].filename.split('.')[1]}')
        save_file(files['task'], "incomming/mytask.py")
        await self.distribute_files_to_slaves(files['data'].filename.split('.')[1])
        await self.start_tasks_on_slaves()
        return {'response': 'Main received files.'}
    
    async def handle_slave_file_upload(self, files):
        os.makedirs("test_incomming", exist_ok=True)
        dataset_extension = files['data'].filename.split('.')[-1]
        
        # Save dataset and task files
        save_file(files['data'], f"test_incomming/data.{dataset_extension}")
        save_file(files['task'], "test_incomming/mytask.py")
        
        return {'response': 'Slave received files successfully'}

    async def distribute_files_to_slaves(self, dataset_extension):
        tasks = [self.send_files(host, dataset_extension) for host in self.slave_hosts]
        await asyncio.gather(*tasks)

    async def start_task(self, host, index):
        """
        Отправляет задание на slave-сервер.
        """
        url = f'http://{host}/task'
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:  # увеличим тайм-аут до 60 секунд
                async with session.post(url, json={'index': index}) as response:
                    return await response.read()
        except asyncio.TimeoutError:
            print(f"Запрос к {host} завершился тайм-аутом.")
            return None
        except aiohttp.ClientError as e:
            print(f"Ошибка при подключении к {host}: {e}")
            return None

    async def start_tasks_on_slaves(self):
        """
        Асинхронно запускает задания на всех slave-серверах.
        """
        tasks = []
        for index, host in enumerate(self.slave_hosts):
            task = asyncio.create_task(self.start_task(host, index))
            tasks.append(task)
        
        done, pending = await asyncio.wait(tasks, timeout=60)  # увеличим общий тайм-аут ожидания до 60 секунд
        
        for future in done:
            if future.exception():
                print(f"Ошибка в выполнении задачи: {future.exception()}")
            else:
                print(f"Результат: {future.result()}")

    async def send_files(self, host, dataset_extension):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'http://{host}/slave_upload_files',
                data={'data': open(f'incomming/data.{dataset_extension}', 'rb'),
                      'task': open('incomming/mytask.py', 'rb')}
            ) as response:
                return await response.read()

    async def send_results(self, host, results):
        with open('results.txt', 'w') as rf:
            rf.write(f'{results}')
        async with aiohttp.ClientSession() as session:
            async with session.post(f'http://{host}/results', data={'results': open('results.txt', 'rb')}) as response:
                return await response.read()

    async def save_results(self, file):
        os.makedirs("output", exist_ok=True)
        save_file(file, "output/results.txt")
