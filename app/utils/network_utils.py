import socket
import aiohttp
from routes import main_routes

import asyncio

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

async def notify_main_server(server_url: str, meta_data: str, result: str):
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
    try:
        slave_ip = f"{socket.gethostbyname(socket.gethostname())}:{main_routes.g_port}"
        print(f"[from network_utils.py] sending from: {slave_ip}")
        async with aiohttp.ClientSession() as session:
            payload = {
                "meta_data": meta_data,
                "result": result,
                "slave_ip": slave_ip
            }
            async with session.post(server_url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to notify server: {response.status}"}
    except Exception as e:
        return {"error": str(e)}