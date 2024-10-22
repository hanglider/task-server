import asyncio
import aiohttp
import flask

async def main():
    url = 'http://192.168.1.102:5000/upload_task'
    with open('C:/Users/zvnlxn/Desktop/task.txt', 'rb') as upl_f:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data={'key': upl_f}) as response:
                return await response.read()
                
asyncio.run(main())  # Assuming you're using python 3.7+
print('отправлено нах')
