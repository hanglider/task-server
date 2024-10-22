import asyncio
import aiohttp
import flask

server_ip1 = input("Введите IP сервера1: ")
server_ip2 = input("Введите IP сервера2: ")

async def main(server_ip):
    url = f'http://{server_ip}:5000/upload_task'
    with open('C:/Users/zvnlxn/Desktop/task.txt', 'rb') as upl_f:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data={'key': upl_f}) as response:
                return await response.read()
                
                
asyncio.run(main(server_ip1))
print('отправлено на server_ip1')
asyncio.run(main(server_ip2))
print('отправлено на server_ip2')

