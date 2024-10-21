import aiohttp
import asyncio

async def process_task(server_ip):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://{server_ip}:5000/task') as response:
            print(f"Response payload: {await response.read()}") #Response message
            print(f"Status: {response.status}") #Status code. If the status is 202,it means that the server has received the message
    return response.status

async def main():
    status = await process_task("192.168.1.122")
    if status == 202:
        print("task has been received")
    else:
        print("something went wrong")
    #TODO: write remaining client code

if __name__ == "__main__":
    asyncio.run(main())
