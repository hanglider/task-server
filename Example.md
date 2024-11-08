Чтобы добавить логи в `.json` файл для отслеживания действий в вашей клиент-серверной системе, можно реализовать функцию логирования, которая будет сохранять ключевые события (например, загрузка файлов, начало и завершение задач) в формате JSON. Примерная структура логов может включать метки времени, имена событий и другие важные сведения.

### Шаги для создания системы логов

1. **Создать функцию для записи логов**:
   Создадим функцию `log_event`, которая принимает название события и дополнительные данные, записывая их в файл JSON.

2. **Добавить вызов логирования в важные части кода**:
   Вызовы функции `log_event` разместим в тех местах кода, где происходят основные события, такие как начало обработки задания, загрузка файлов и отправка результатов.

### Реализация

Добавим новый файл `logger.py` для управления логами и внесем изменения в код других файлов для вызова логирования. 

#### logger.py
```python
import json
import os
from datetime import datetime

LOG_FILE = "system_logs.json"

def log_event(event_name, details=None):
    """Записывает событие в JSON файл логов."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_name,
        "details": details or {}
    }

    # Проверка на существование файла, чтобы инициализировать массив JSON при первой записи
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as file:
            json.dump([], file)

    # Чтение существующих логов и добавление новой записи
    with open(LOG_FILE, "r+") as file:
        logs = json.load(file)
        logs.append(log_entry)
        file.seek(0)
        json.dump(logs, file, indent=4)
```

#### Пример использования `log_event` в других файлах

Теперь добавим вызов `log_event` в соответствующие места, чтобы логировать события, такие как обработка задания и загрузка файлов.

##### task_manager.py
```python
from logger import log_event
# Добавьте вызовы log_event в местах, где происходят ключевые события

async def handle_main_file_upload(self, files):
    log_event("Main file upload received", {"files": list(files.keys())})
    await asyncio.sleep(7)
    log_event("Files processed", {"status": "completed"})
    return {'response': 'Main received files.'}

async def distribute_files_to_slaves(self, dataset_extension):
    log_event("Distributing files to slaves", {"extension": dataset_extension})
    tasks = [self.send_files(host, dataset_extension) for host in self.slave_hosts]
    await asyncio.gather(*tasks)

async def send_results(self, host, results):
    log_event("Sending results to host", {"host": host})
    with open('results.txt', 'w') as rf:
        rf.write(f'{results}')
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://{host}/results', data={'results': open('results.txt', 'rb')}) as response:
            log_event("Results sent", {"host": host, "status": response.status})
            return await response.read()
```

##### server_routes.py
```python
from logger import log_event

@app.route("/task", methods=['POST', 'GET'])
async def receive_task():
    data = request.json
    index_part = data['index']
    log_event("Task received", {"index_part": index_part})
    await task_manager.process_task(index_part)
    return jsonify({"response": "The task has started to be processed."}), 202

@app.route('/main_upload_files', methods=['POST'])
async def main_receive_files():
    log_event("Main upload files request received")
    task = asyncio.create_task(task_manager.handle_main_file_upload(request.files))
    return jsonify({'response': 'Files received for processing'})
```

#### Обработка логов при аварийном завершении

Чтобы узлы могли восстанавливать сеть после аварийного завершения, можно записывать более детальные логи с состояниями каждой задачи.