import json
from datetime import datetime

def log_action(message: str, log_file: str = "log.json"):
    """
    Записывает сообщение лога в JSON файл.

    :param message: Сообщение, которое нужно записать в лог.
    :param log_file: Путь к файлу лога (по умолчанию log.json).
    """
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message
    }

    # Проверяем, существует ли файл и нужно ли добавлять запятую
    try:
        with open(log_file, "rb+") as f:
            f.seek(-1, 2)  # Переходим к последнему символу в файле
            last_char = f.read(1)
            if last_char == b"]":  # Если файл заканчивается на "]", корректируем
                f.seek(-1, 2)
                f.write(b",")  # Добавляем запятую перед новой записью
            else:  # Если файла нет или он пустой
                raise FileNotFoundError
    except (FileNotFoundError, OSError):
        # Если файл не найден или пустой, создаем новый массив
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("[")

    # Записываем новую запись
    with open(log_file, "a", encoding="utf-8") as f:
        json.dump(log_entry, f, ensure_ascii=False)
        f.write("]")  # Закрываем массив логов
