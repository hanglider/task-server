# TODO: Сделать heartbeat
import socket
import aiohttp



async def notify_main_server(server_url: str, task_id: str, result: str):
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
        slave_ip = f"{socket.gethostbyname(socket.gethostname())}:5001"
        print(f"local ip address(slave): ${slave_ip}:5001")

        async with aiohttp.ClientSession() as session:
            payload = {
                "task_id": task_id,
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