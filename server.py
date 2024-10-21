from flask import Flask, jsonify
import asyncio
from asgiref.wsgi import WsgiToAsgi
from taskprocessor import TaskProcessor
import mytask

app = Flask(__name__)

@app.route("/task", methods=['POST'])
async def receive_task():
    asyncio.create_task(process_task())
    
    return jsonify({"response": "The task has started to be processed."}), 202

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


asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(asgi_app, host='192.168.1.122', port=5000)
