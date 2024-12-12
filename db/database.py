import os
import socket
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from databases import Database
import zipfile
import io
from typing import List
import aiofiles
import time

# Конфигурация
UPLOAD_FOLDER = "db\storage"
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
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_downloaded INTEGER DEFAULT 0,
        status TEXT DEFAULT 'waiting'
    )
    """
    await database.execute(query)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    filenames = []
    count = len(os.listdir(UPLOAD_FOLDER))
    data_name, data_path, task_name, task_path = None, None, None, None

    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Invalid file name.")

        filename = f"{file.filename.split('.')[0]}_{count + 1}.{file.filename.split('.')[-1]}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        try:
            async with aiofiles.open(filepath, 'wb') as f:
                contents = await file.read()
                await f.write(contents)
            if ".py" in filename:
                task_name, task_path = filename, filepath
            else:
                data_name, data_path = filename, filepath
            filenames.append(filepath)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
        finally:
            await file.close()

    if not task_name or not task_path or not data_name or not data_path:
        raise HTTPException(status_code=400, detail="Missing required files.")

    query = """
    INSERT INTO file_metadata (task_name, task_path, data_name, data_path, is_downloaded)
    VALUES (:task_name, :task_path, :data_name, :data_path, :is_downloaded)
    """
    values = {
        "task_name": task_name,
        "task_path": task_path,
        "data_name": data_name,
        "data_path": data_path,
        "is_downloaded": 0,
    }

    try:
        await database.execute(query, values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"filenames": filenames}



@app.get("/download")
async def download_file():
    # Modify the query to select the file with the earliest upload_date
    query = """
    SELECT task_name, task_path, data_name, data_path, is_downloaded, id FROM file_metadata 
    WHERE is_downloaded = 0 
    ORDER BY upload_date ASC LIMIT 1
    """
    result = await database.fetch_one(query=query)
    
    if not result:
        raise HTTPException(status_code=404, detail="No files available for download.")
    
    task_name = result["task_name"]
    task_path = result["task_path"]
    data_name = result["data_name"]
    data_path = result["data_path"]
    is_downloaded = result["is_downloaded"]
    record_id = result["id"]
    
    # Check if the task and data files exist
    if not task_name or not os.path.exists(task_path):
        raise HTTPException(status_code=404, detail=f"Task file '{task_name}' not found on server.")
    
    if not data_name or not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail=f"Data file '{data_name}' not found on server.")
    
    # If the files have already been downloaded
    if is_downloaded:
        raise HTTPException(status_code=400, detail=f"Files '{task_name}' and '{data_name}' have already been downloaded.")

    # Update the database to mark the files as downloaded
    update_query = """
    UPDATE file_metadata
    SET is_downloaded = 1, status = 'processing'
    WHERE id = :id
    """
    await database.execute(query=update_query, values={"id": record_id})

    # Create a ZIP archive
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_archive:
        zip_archive.write(task_path, arcname=task_name)
        zip_archive.write(data_path, arcname=data_name)
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={task_name}_and_{data_name}.zip", 
                  "X-Task-ID": str(record_id)}
    )

@app.put("/update_status")
async def update_status(task_id: int):
    if not task_id:
        raise HTTPException(status_code=400, detail="Task ID and status are required.")
    
    # Обновление статуса в базе данных
    query = """
    UPDATE file_metadata
    SET status = :status
    WHERE id = :task_id
    """
    values = {"status": 'completed', "task_id": task_id}

    try:
        result = await database.execute(query, values)
        if result == 0:
            raise HTTPException(status_code=404, detail="Task not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {"message": "Task status updated successfully", "task_id": task_id}

if __name__ == "__main__":
    import uvicorn
    name = socket.gethostname()
    host = socket.gethostbyname(name)
    uvicorn.run(app, host=host, port=8000)
