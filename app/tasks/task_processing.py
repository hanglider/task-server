import asyncio
import aiohttp
from app.tasks.task_manager import task_manager

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
        
    def __init__(self, timeout : 10):
        self.tasks = []
        self.timeout = timeout

    def add_task(self, func, *args, **kwargs):
        task = asyncio.create_task(func(*args, **kwargs))
        self.tasks.append(task)

    async def run_all_tasks(self):
        results = []
        done, pending = await asyncio.wait(self.tasks, timeout=self.timeout)
        for future in done:
            value = future.result()
            results.append(value)
        if len(pending) != 0:
            raise TimeoutError("The task has been running for too long")
        return results

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
    # TODO: process_task with taskprocessor
    print("Task processed")
