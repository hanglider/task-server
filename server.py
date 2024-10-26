from flask import Flask, jsonify, request
import asyncio
from asgiref.wsgi import WsgiToAsgi
from taskprocessor import TaskProcessor
import aiohttp
import os

app = Flask(__name__)

all_results = []
num_splits = 1  # Количество частей, на которые была разделена задача

received_file_index = 0


# output_dir = 'output/'
# output_file = os.path.join(output_dir, 'merged_output.txt')

def merge_results(task_parts):
    merged_result = ""
    for part in task_parts:
        merged_result += part
    return merged_result

slave_hosts = ['192.168.206.54:5001']

@app.route("/task", methods=['POST', 'GET'])
async def receive_task():
    data = request.json
    index_part = data['index']
    asyncio.create_task(process_task(index_part))
    
    return jsonify({"response": "The task has started to be processed."}), 202

@app.route('/main_upload_files', methods=['POST'])
async def main_receive_files():
    data = request.files

    os.makedirs("incomming", exist_ok=True)
    data['data'].save(f'incomming/data.{data['data'].filename.split('.')[1]}') 
    data['task'].save('incomming/mytask.py')
    dataset_extension = f'{data['data'].filename.split('.')[1]}'

    tasks = []
    for host in slave_hosts:
        task = asyncio.create_task(send_files(host, dataset_extension))
        tasks.append(task)
    done, _ = await asyncio.wait(tasks, timeout=40)
    responses = []
    for future in done:
        value = future.result()
        responses.append(value)
        print(value)

    tasks = []   
    if len(responses) == num_splits:
        index = 0
        for host in slave_hosts:
            task = asyncio.create_task(start_task(host, index))
            index += 1
            tasks.append(task)
            
        done, _ = await asyncio.wait(tasks, timeout=40)
        for future in done:
            result = future.result()
            print(f"Результаты: {result}")
        
        
    return jsonify({'response': 'Main received files.'})

async def start_task(host, index):
    url = f'http://{host}/task'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={'index' : index}) as response:
            return await response.read()

@app.route('/slave_upload_files', methods=['POST', 'GET'])
async def slave_receive_files():
    data = request.files
    os.makedirs("test_incomming", exist_ok=True)
    data['data'].save(f'test_incomming/data.{data['data'].filename.split('.')[1]}') 
    data['task'].save('test_incomming/mytask.py')

    return jsonify({'response': 'Slave received files.'}) 

async def send_files(host, dataset_extension):
    try:
        task =  open('incomming/mytask.py', 'rb')
    except (OSError, IOError) as e:
        return e

    try:
        data = open(f'incomming/data.{dataset_extension}', 'rb')
    except (OSError, IOError) as e:
        return e

    url = f'http://{host}/slave_upload_files'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={'data' : data, 'task' : task}) as response:
            return await response.read()

async def process_task(index_part):
    from incomming import mytask
    image_parts = mytask.load_image("test_incomming/data.jpg", num_splits)
    main = mytask.main
    task_processor = TaskProcessor(timeout=10)
    task_processor.add_task(main, image_parts[index_part])
    results = await task_processor.run_all_tasks()
    print(len(results))
    
    # TODO: send results to the main node
    task_send_results = asyncio.create_task(send_results('192.168.206.54:5000', results))
    await task_send_results

    print(f"Processed {len(results)} results")

@app.route('/results', methods=['POST'])
async def receive_results():
    data = request.files
    os.makedirs("output", exist_ok=True)
    data['results'].save("output/results.txt")
    # if len(all_results) == num_splits:

    #     os.makedirs('output', exist_ok=True)
        
    #     merged_file = merge_results(all_results)
    #     print(f'СМЕРЖЕННЫЙ ФАЙЛ {merged_file}')
    #     # TODO: сохранение файла в зависимости от переданного формата
    #     # if not os.path.exists(output_dir):
    #     #     os.makedirs(output_dir)

    #     # merged_image = merge_results(all_results)
    #     # cv2.imwrite('output.jpg', merged_image)

    #     print("Image has been merged and saved as 'output.jpg'")

    return jsonify({'response': 'Results received'}), 200

async def send_results(host, results):
    url = f'http://{host}/results'

    with open('results.txt', 'w') as rf:
        rf.write(f'{results}')

    with open('results.txt', 'rb') as rf:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data={'results': rf}) as response:
                return await response.read()


asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    import uvicorn
    import socket
    name = socket.gethostname()
    host = socket.gethostbyname(name)
    uvicorn.run(asgi_app, host='192.168.206.54', port=5000)