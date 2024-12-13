from fastapi import FastAPI, UploadFile, File
import aiofiles
import os

app = FastAPI()
RESULTS_DIR = "client_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.post("/receive_results")
async def receive_results(file: UploadFile = File(...)):
    saved_files = []
    async with aiofiles.open(f"client_results/{file.filename}", "wb") as f:
        content = await file.read()
        await f.write(content)
    saved_files.append(f"client_results/{file.filename}")
    return {"status": "success", "saved_files": saved_files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.3.12", port=5002)
