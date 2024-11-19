from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.file_utils import save_uploaded_files
from tasks.task_processing import process_task
import asyncio
import os
from typing import List

router = APIRouter()


@router.post('/slave_upload_files')
async def slave_upload(files: List[UploadFile] = File(...)):
    os.makedirs("test_incoming", exist_ok=True)
    filenames = await save_uploaded_files(files, "test_incoming")

    asyncio.create_task(process_task())
    return {"message": "Files successfully uploaded"}
