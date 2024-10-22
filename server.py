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
    print(f"Получено сообщение: {data['key']}, Тип: {type(data['key'])}")     

    #TODO: save file to server


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

def send_response(main_server_ip):
    file = 'task.py'
    url = f"http://{main_server_ip}:5000/message'"
    try:
        f = open("task.py")
       # data = request.files()
        response = request.post(url)
    except:
        pass

    # url = f'http://{server_ip}:5000/message'
    # data = {'message': message}
    # crop = [{0:500, 0:500}, {500:1000, 500:1000}]
    # data['message'] = crop[index]
    # try:
    #     response = requests.post(url, json=data)
    #     if response.status_code == 200:
    #         print(f"Ответ от сервера: {response.json()['response']}")
    #     else:
    #         print(f"Ошибка сервера: {response.status_code}")
    # except Exception as e:
    #     print(f"Ошибка подключения: {e}")

def send_message():
    pass
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(asgi_app, host='172.20.10.2', port=5000)
