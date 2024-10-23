from flask import Flask, jsonify, request
import asyncio
from asgiref.wsgi import WsgiToAsgi
from taskprocessor import TaskProcessor
import mytask

app = Flask(__name__)

@app.route("/task", methods=['POST'])
async def receive_task():
    asyncio.create_task(process_task())
    
    return jsonify({"response": "The task has started to be processed."}), 202

@app.route('/upload_task', methods=['POST'])
async def receive_file():
    data = request.files  # Получаем данные из POST-запроса
    print(f"Получено сообщение: {data['task']}, {data['data']}")
    data['data'].save(f'incomming/data.{data['data'].filename.split('.')[1]}') 
    data['task'].save('incomming/task.py') 
    return jsonify({'response': 'Сообщение получено!'})  # Возвращаем ответ клиенту

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

def send_message():
    pass
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    import uvicorn
    import socket
    name = socket.gethostname()
    host = socket.gethostbyname(name)
    uvicorn.run(asgi_app, host=host, port=5000)
    send_response(host)
