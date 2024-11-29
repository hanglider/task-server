import asyncio
import aiohttp
from typing import List


class Heartbeat:
    def __init__(self, node_type: str, main_server_url: str = None, slave_urls: List[str] = None):
        """
        Инициализация Heartbeat.

        :param node_type: Тип узла ('main' или 'slave').
        :param main_server_url: URL основного сервера (если этот узел - slave).
        :param slave_urls: Список URL-адресов узлов slave (если этот узел - main).
        """
        self.node_type = node_type
        self.main_server_url = main_server_url
        self.slave_urls = slave_urls or []

    async def _send_heartbeat(self, url: str) -> bool:
        """
        Отправляет heartbeat на указанный URL.

        :param url: URL-адрес узла.
        :return: True, если узел отвечает, иначе False.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/heartbeat") as response:
                    if response.status == 200:
                        return True
        except Exception as e:
            print(f"Error connecting to {url}: {e}")
        return False

    async def _check_slaves(self):
        """
        Проверяет доступность узлов slave.
        """
        print("Checking slave nodes...")
        for url in self.slave_urls:
            if await self._send_heartbeat(url):
                print(f"Slave {url} is alive")
            else:
                print(f"Slave {url} is down")

    async def _notify_main(self):
        """
        Отправляет heartbeat основному серверу.
        """
        if await self._send_heartbeat(self.main_server_url):
            print("Main server is alive")
        else:
            print("Main server is down")

    async def start(self, interval: int = 10):
        """
        Запускает процесс Heartbeat.

        :param interval: Интервал между проверками (в секундах).
        """
        while True:
            if self.node_type == 'main':
                await self._check_slaves()
            elif self.node_type == 'slave':
                await self._notify_main()
            await asyncio.sleep(interval)
