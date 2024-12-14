import socket
import aiohttp
import requests
from routes import main_routes

import asyncio


DB_IP = "192.168.1.107:8001"


async def new_main():
    print("Main server is down. Starting new main server...")
    # запуск нового основного сервера

async def send_heartbeat(server_url: str, interval: int = 15):
    while True:
        try:
            # Получение IP-адреса узла
            slave_ip = f"{socket.gethostbyname(socket.gethostname())}:5001"
            print(f"Sending heartbeat from {slave_ip}")

            # Отправка POST-запроса
            async with aiohttp.ClientSession() as session:
                payload = {"slave_ip": slave_ip}
                async with session.post(server_url, json=payload) as response:
                    if response.status != 200:
                        print(f"Heartbeat failed: {response.status}")
                        response_text = await response.text()
                        print(f"Response text: {response_text}")
                    else:
                        print(f"Heartbeat successful: {response.status}")
        except aiohttp.ClientError as e:
            print(f"Heartbeat error: {str(e)}")
            await new_main()
        except Exception as e:
            print(f"Heartbeat error: {str(e)}")
        await asyncio.sleep(interval)


async def scan_for_main():
    await asyncio.sleep(1)
    data = await asyncio.create_task(get_ips(main_routes.HOSTS_DB))
    
    # Проверка, найден ли 'db' в данных
    for ip, info in data.items():
        if info.get("label") == 'main':
            main_ip = ip
            print(f"Slave IP найден: {main_ip}")
            return main_ip  # Возвращаем IP и выходим из цикла

async def notify_main_server(meta_data: str, result: str):
    """
    Sends a notification to the main server that the task has been processed,
    along with the IP address of the slave node.

    Args:
        server_url (str): The main server's URL to send the notification to.
        task_id (str): The unique identifier of the processed task.
        result (str): The result of the task processing.

    Returns:
        dict: The response from the main server.
    """
    main_ip = await scan_for_main()
    try:
        slave_ip = f"{socket.gethostbyname(socket.gethostname())}:{main_routes.g_port}"
        print(f"[from network_utils.py] sending from: {slave_ip}")
        async with aiohttp.ClientSession() as session:
            payload = {
                "meta_data": meta_data,
                "result": result,
                "slave_ip": slave_ip
            }
            async with session.post(f"http://{main_ip}/task_completed", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to notify server: {response.status}"}
    except Exception as e:
        return {"error": str(e)}
    
async def send_log(log: str, server_url: str):
    """
    Отправляет лог на сервер по указанному IP.

    :param ip: IP-адрес, для которого добавляется лог
    :param log: Лог-сообщение
    :param server_url: URL сервера, на который отправляется запрос
    """
    async with aiohttp.ClientSession() as session:
        port = main_routes.g_port
        host = main_routes.g_host
        url = f"http://{server_url}/add_log/{host}:{port}"
        payload = {"log": log}

        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Успешно добавлено: {result}")
                else:
                    error_detail = await response.json()
                    print(f"Ошибка {response.status}: {error_detail['detail']}")
        except aiohttp.ClientError as e:
            print(f"Ошибка соединения: {e}")

async def get_ips(server_url: str):
    """
    Получает список всех IP-адресов с сервера.

    :param server_url: URL сервера, на который отправляется запрос
    """
    async with aiohttp.ClientSession() as session:
        url = f"http://{server_url}/get_ips"

        try:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    # print(f"Список IP-адресов: {result['ips']}")
                    return result['ips']
                else:
                    print(f"Ошибка {response.status}: Не удалось получить список IP-адресов")
        except aiohttp.ClientError as e:
            print(f"Ошибка соединения: {e}")

def send_ip_to_server(host, port):
    # Получаем свой IP-адрес

    # Данные для отправки
    client_ip = f"{host}:{port}"
    data = {"ip": client_ip}
    
    try:
        # Отправляем запрос на сервер
        response = requests.post(f"http://{DB_IP}/add_ip", json=data)
        
        # Проверяем статус код ответа
        if response.status_code == 200:
            print(f"IP {client_ip} успешно отправлен на сервер.")
            return response.json()  # Возвращаем ответ от сервера
        else:
            print(f"Ошибка при отправке IP: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке IP: {e}")
        return None