from fastapi import FastAPI, UploadFile, File, HTTPException
from task_manager import TaskManager
import aiofiles
from typing import List
import time as t
import os

app = FastAPI()
task_manager = TaskManager()

@app.route("/task", methods=['POST', 'GET'])
async def receive_task():
    data = request.json
    index_part = data['index']
    await task_manager.process_task(index_part)
    return jsonify({"response": "The task has started to be processed."}), 202

@app.post("/main_upload_files")
async def upload(files: List[UploadFile] = File(...)):
    os.makedirs("incomming", exist_ok=True)
    filenames = []
    for file in files:
        try:
            contents = await file.read()
            with open(f"incomming/{file.filename}", 'wb') as f:
                f.write(contents)
            filenames.append(file.filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Something went wrong: {str(e)}')
        finally:
            await file.close()

    return {"message": f"Successfully uploaded {filenames}"}

# @app.route('/main_upload_files', methods=['POST'])
# async def main_receive_files():
#     print(f"Время получения сообщения: {t.time():2.f}")
#     # task = asyncio.create_task(task_manager.handle_main_file_upload(request.files))
#     # response = await task
#     return {"response": "main received files"}

@app.route('/slave_upload_files', methods=['POST', 'GET'])
async def slave_receive_files():
    response = await task_manager.handle_slave_file_upload(request.files)
    return jsonify(response)

@app.route('/results', methods=['POST'])
async def receive_results():
    await task_manager.save_results(request.files['results'])
    return jsonify({'response': 'Results received'}), 200
