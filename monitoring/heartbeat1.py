import asyncio
import aiohttp
import time
from typing import List




###################################################################################
##########################                          ###############################
##########################   Используй heartbeat2   ###############################
##########################                          ###############################
###################################################################################


#check_interval: int = 10    время через сколько происходит опрос
#timeout: int = 5            время в течении которого node должен ответить


class Heartbeat:
    def __init__(self, node_type: str, main_server_url: str = None, slave_urls: List[str] = None, 
                 check_interval: int = 10, timeout: int = 5):
        """
        Heartbeat system to monitor main and slave nodes.

        Args:
            node_type (str): 'main' for the main node or 'slave' for a worker node.
            main_server_url (str): URL of the main server (for slave nodes).
            slave_urls (List[str]): List of slave node URLs (for main node).
            check_interval (int): Interval (in seconds) between heartbeat checks.
            timeout (int): Timeout (in seconds) for responses.
        """
        self.node_type = node_type
        self.main_server_url = main_server_url
        self.slave_urls = slave_urls or []
        self.check_interval = check_interval
        self.timeout = timeout
        self.last_main_heartbeat = time.time()

    async def check_slaves(self):
        """Check the availability of slave nodes."""
        for index, slave_url in enumerate(self.slave_urls):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{slave_url}/heartbeat", timeout=self.timeout) as response:
                        if response.status == 200:
                            print(f"Slave {slave_url} is alive.")
            except Exception:
                print(f"Slave {slave_url} is down.")
                await self.node_is_fall(index)

    async def monitor_main(self):
        """Monitor the main node by checking the last heartbeat received."""
        while True:
            if time.time() - self.last_main_heartbeat > self.check_interval + self.timeout:
                print("Main node is down.")
                await self.pick_new_main_node()
                break
            await asyncio.sleep(self.check_interval)

    async def send_heartbeat_to_main(self):
        """Send a heartbeat signal to the main server."""
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.main_server_url}/heartbeat", timeout=self.timeout) as response:
                        if response.status == 200:
                            print("Heartbeat sent to main server.")
            except Exception:
                print("Failed to send heartbeat to main server.")
            await asyncio.sleep(self.check_interval)

    async def node_is_fall(self, index: int):
        """Handle a fallen slave node."""
        print(f"Node at index {index} has fallen. Taking appropriate actions.")
        # Custom logic for handling fallen nodes.

    async def pick_new_main_node(self):
        """Handle the failure of the main node."""
        print("Electing a new main node.")
        # Custom logic for main node election.

    async def start(self):
        """Start the heartbeat system based on the node type."""
        if self.node_type == 'main':
            while True:
                await self.check_slaves()
                await asyncio.sleep(self.check_interval)
        elif self.node_type == 'slave':
            asyncio.create_task(self.monitor_main())
            await self.send_heartbeat_to_main()

# Example usage for main node
# heartbeat = Heartbeat(node_type='main', slave_urls=['http://192.168.1.101:5001', 'http://192.168.1.102:5001'])
# asyncio.run(heartbeat.start())

# Example usage for slave node
# heartbeat = Heartbeat(node_type='slave', main_server_url='http://192.168.1.107:5000')
# asyncio.run(heartbeat.start())