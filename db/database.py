import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from databases import Database

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
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL UNIQUE,
        upload_date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """
    await database.execute(query)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # try:
    file_path = f"{UPLOAD_FOLDER}/{os.path.basename(file.filename)}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"message": "File uploaded successfully"}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")



@app.get("/download/{file_id}")
async def download_file(file_id: int):

    query = """
    SELECT file_name, file_path FROM file_metadata WHERE id = :file_id
    """
    result = await database.fetch_one(query=query, values={"file_id": file_id})
    
    if not result:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_name, file_path = result["file_name"], result["file_path"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(file_path, filename=file_name, media_type="application/octet-stream")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="172.20.10.2", port=8000)