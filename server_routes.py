from flask import Flask, jsonify, request
from task_manager import TaskManager
import asyncio
import time as t

app = Flask(__name__)
task_manager = TaskManager()

@app.route("/task", methods=['POST', 'GET'])
async def receive_task():
    data = request.json
    index_part = data['index']
    await task_manager.process_task(index_part)
    return jsonify({"response": "The task has started to be processed."}), 202

@app.route('/main_upload_files', methods=['POST'])
async def main_receive_files():
    print(f"Время получения сообщения{t.time()}")
    task = asyncio.create_task(task_manager.handle_main_file_upload(request.files))
    # response = await task
    return jsonify({'response': 'Results received'})

@app.route('/slave_upload_files', methods=['POST', 'GET'])
async def slave_receive_files():
    response = await task_manager.handle_slave_file_upload(request.files)
    return jsonify(response)

@app.route('/results', methods=['POST'])
async def receive_results():
    await task_manager.save_results(request.files['results'])
    return jsonify({'response': 'Results received'}), 200
