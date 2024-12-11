import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from databases import Database
import zipfile
import io
from typing import List
import aiofiles
import time

# TODO: чтобы клиент на бд отсылал свой ip чтобы потом туда возвращать результаты

# Конфигурация
UPLOAD_FOLDER = "database/storage"
DB_URL = "sqlite:///file_metadata.db"

# Создание папки для хранения файлов
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Инициализация FastAPI и базы данных
app = FastAPI()
database = Database(DB_URL)


# Инициализация базы данных при запуске сервера
@app.on_event("startup")
async def startup():
    await database.connect()
    query = """
    CREATE TABLE IF NOT EXISTS file_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT NOT NULL,
        task_path TEXT NOT NULL UNIQUE,
        data_name TEXT NOT NULL,
        data_path TEXT NOT NULL UNIQUE,
        upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
        is_downloaded INTEGER DEFAULT 0
    )
    """
    await database.execute(query)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    print(time.time())
    os.makedirs("db/storage", exist_ok=True)
    filenames = []
    count = len(os.listdir('db/storage'))
    for file in files:
        try:
            filename = f"{file.filename.split('.')[0]}{count}.{file.filename.split('.')[-1]}"
            filepath = f"db/storage/{filename}"
            async with aiofiles.open(filepath, 'wb') as f:
                contents = await file.read()
                await f.write(contents)
            filenames.append(filepath)
            print(os.listdir('db/storage'))

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file {file.filename}: {str(e)}")
        finally:
            await file.close()    
    return filenames

@app.get("/download")
async def download_file():

    query = """
    SELECT task_name, task_path, data_name, data_path, id FROM file_metadata WHERE is_downloaded = 0 LIMIT 1
    """
    result = await database.fetch_one(query=query)
    
    if not result:
        raise HTTPException(status_code=404, detail="File not found")
    
    task_name, task_path, data_name, data_path, is_downloaded, id = result["task_name"], result["task_path"], result["data_name"], result["data_path"], result["is_downloaded"], result["id"]
    
    if not os.path.exists(task_path):
        raise HTTPException(status_code=404, detail="Task file not found on server")
    
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Data file not found on server")
    
    if is_downloaded:
        return {"message": f"File {task_name} and {data_name} has already been downloaded."}
    
    update_query = """
    UPDATE file_metadata
    SET is_downloaded = 1
    WHERE id = :id
    """
    # TODO: можно хранить инфу о состоянии файла (ожидает обработки, обрабатывается и готов)

    await database.execute(query=update_query, values={"id": id})

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_archive:
        zip_archive.write(task_path, arcname=task_name)
        zip_archive.write(data_path, arcname=data_name)
    zip_buffer.seek(0)

    # Streaming the ZIP file as a response
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={task_name}_and_{data_name}.zip"}
    )




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.3.12", port=8000)