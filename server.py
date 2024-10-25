from flask import Flask, jsonify, request
import asyncio
from asgiref.wsgi import WsgiToAsgi
from taskprocessor import TaskProcessor
import mytask
import aiohttp
import os

app = Flask(__name__)

all_results = []
num_splits = 2  # Количество частей, на которые была разделена задача

output_dir = 'output/'
output_file = os.path.join(output_dir, 'merged_output.txt')

def merge_results(task_parts):
    merged_result = ""
    for part in task_parts:
        merged_result += part
    return merged_result

hosts = ['192.168.1.107:5001', '192.168.1.107:5002']

@app.route("/task", methods=['POST'])
async def receive_task():
    asyncio.create_task(process_task())
    
    return jsonify({"response": "The task has started to be processed."}), 202

@app.route('/main_upload_files', methods=['POST'])
async def main_receive_files():
    data = request.files

    os.mkdir("incomming")
    data['data'].save(f'incomming/data.{data['data'].filename.split('.')[1]}') 
    data['task'].save('incomming/task.py')
    dataset_extension = f'{data['data'].filename.split('.')[1]}'

    tasks = []
    for host in hosts:
        task = asyncio.create_task(send_files(host, dataset_extension))
        tasks.append(task)
    done, _ = await asyncio.wait(tasks, timeout=40)
    for future in done:
        value = future.result()
        print(value)
    
    return jsonify({'response': 'Main received files.'})

@app.route('/slave_upload_files', methods=['POST', 'GET'])
async def slave_receive_files():
    data = request.files
    data['data'].save(f'incomming/data.{data['data'].filename.split('.')[1]}') 
    data['task'].save('incomming/task.py')

    return jsonify({'response': 'Slave received files.'}) 

async def send_files(host, dataset_extension):
    try:
        task =  open('incomming/task.py', 'rb')
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

async def process_task():
    num_splits = 2
    image_parts = mytask.load_image("negr.jpg", num_splits)
    main = mytask.main
    task_processor = TaskProcessor(timeout=10)
    for i in range(num_splits):
        task_processor.add_task(main, image_parts[i])
    results = await task_processor.run_all_tasks()
    print(len(results))
    #TODO: send results to the main node
    await send_results('192.168.1.107:5000', results)  # IP главного сервера

    print(f"Processed {len(results)} results")

# def merge_results(image_parts, image_height):
#     import numpy as np
#     merged_image = np.zeros((image_height, image_parts[0].shape[1]), dtype=np.uint8)

#     y_offset = 0
#     for part in image_parts:
#         merged_image[y_offset:y_offset + part.shape[0], :] = part
#         y_offset += part.shape[0]
    
#     return merged_image

# @app.route('/results', methods=['POST'])
# async def receive_results():
#     data = await request.get_json()
#     print(f"Received processed data: {data}")
#     return jsonify({'response': 'Results received'}), 200

@app.route('/results', methods=['POST'])
async def receive_results():
    data = await request.get_json()
    all_results.append(data)  

    if len(all_results) == num_splits:  

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        merged_image = merge_results(all_results)
        cv2.imwrite('output.jpg', merged_image)

        print("Image has been merged and saved as 'output.jpg'")

    return jsonify({'response': 'Results received'}), 200

async def send_results(host, results):
    url = f'http://{host}/results'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=results) as response:
            return await response.read()


asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    import uvicorn
    import socket
    name = socket.gethostname()
    host = socket.gethostbyname(name)
    uvicorn.run(asgi_app, host=host, port=5000)
