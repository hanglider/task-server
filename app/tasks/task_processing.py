import asyncio
import os
import aiohttp
from tasks.task_manager import task_manager
from utils.network_utils import notify_main_server

class TaskProcessor:
    """
    A class to manage and execute multiple asynchronous tasks concurrently.

    Attributes:
        tasks (list): A list to store asyncio.Task objects representing the tasks to be executed.
        timeout (int): The maximum time (in seconds) to wait for tasks to complete before raising a TimeoutError.

    Methods:
        __init__(timeout: int = 10):
            Initializes a TaskProcessor instance with an optional timeout value.
        
        add_task(func, *args, **kwargs):
            Adds a new asynchronous task to the processor. The task is created by calling the provided function
            with the given arguments and keyword arguments.
        
        run_all_tasks() -> list:
            Executes all added tasks concurrently and waits for their completion. If all tasks complete within
            the specified timeout, their results are returned as a list. If any tasks remain pending after the
            timeout, a TimeoutError is raised.
    Example:
        import asyncio

        async def example_task(n):
            await asyncio.sleep(n)
            return f'Task completed after {n} seconds'

        async def main():
            processor = TaskProcessor(timeout=5)
            processor.add_task(example_task, 2)
            processor.add_task(example_task, 3)
            processor.add_task(example_task, 6)  # This will exceed the timeout
            
            try:
                results = await processor.run_all_tasks()
                print(results)
            except TimeoutError as e:
                print(e)

        # To run the example:
        # asyncio.run(main())
    """
        
    def __init__(self, timeout: int = 10):
        self.tasks = []
        self.timeout = timeout

    def add_task(self, func, *args, **kwargs):
        """Add a new async task to the processor."""
        task = asyncio.create_task(func(*args, **kwargs))
        self.tasks.append(task)

    async def run_all_tasks(self):
        """Run all tasks concurrently and wait for completion."""
        done, pending = await asyncio.wait(self.tasks, timeout=self.timeout)

        results = []
        for future in done:
            try:
                results.append(await future)
            except Exception as e:
                print(f"Task failed with error: {e}")

        if pending:
            for task in pending:
                task.cancel()
            raise TimeoutError("Some tasks did not complete within the timeout period.")
        
        return results

async def distribute_files_to_slaves():
    print("Sending files to slaves")
    #TODO: отправить ссылки из task_manager.queue на хост
    if not task_manager.queue:
        print("\033[32mAll task have been completed\033[0m")
        return

    part = task_manager.queue.pop(0)
    data_file = part[0]
    task_file = part[1]

    form_data = aiohttp.FormData()
    form_data.add_field(
        'files', 
        open(task_file, 'rb'), 
        filename=os.path.basename(task_file),  # Используем только имя файла
        content_type='application/octet-stream'
    )
    form_data.add_field(
        'files', 
        open(data_file, 'rb'), 
        filename=os.path.basename(data_file),  # Используем только имя файла
        content_type='application/octet-stream'
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://{task_manager.available_hosts.pop(0)}/slave_upload_files", data=form_data) as response:
            print(await response.json())


async def process_task(dir: str = "incoming", meta_data: str = "error"):
    from test_incoming import task

    processor = TaskProcessor(timeout=10)

    for filename in os.listdir(f"app\{dir}"):
        filepath = os.path.join(f"app\{dir}", filename)
        if os.path.isfile(filepath):
            if "part" in filepath:
                processor.add_task(task.main, task.load_image(filepath, 1)[0]) #TODO: figure out which part of the image we need to process

    try:
        results = await processor.run_all_tasks()
        for i, result in enumerate(results):
            await notify_main_server("http://172.20.10.2:5000/task_completed", meta_data, f"{result}")  #TODO: somehow get main_server_url from outside 
    except TimeoutError as e:
        print("Error processing tasks:", e)