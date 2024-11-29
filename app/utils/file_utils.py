import aiofiles
from fastapi import UploadFile, HTTPException
from typing import List
from urllib.parse import unquote


async def main_save_uploaded_files(files: List[UploadFile], directory: str, index: int = 0) -> List[str]:
    filenames = []
    for file in files:
        try:
            filename = f"{file.filename.split('.')[0]}{index}.{file.filename.split('.')[-1]}"
            filepath = f"app/{directory}/{filename}"
            async with aiofiles.open(filepath, 'wb') as f:
                contents = await file.read()
                await f.write(contents)
            filenames.append(filepath)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file {file.filename}: {str(e)}")
        finally:
            await file.close()
    return filenames

async def slave_save_uploaded_files(files: List[UploadFile], directory: str) -> List[str]:
    filenames = []
    meta_data : str = ""
    for file in files:
        try:
            if 'task' in file.filename:
                filename = f"{file.filename.split('.')[0][:-1]}.{file.filename.split('.')[-1]}"
            if 'part' in file.filename:
                decoded_filename = unquote(file.filename)
                filename = f"{decoded_filename.split('.')[0][:4]}.{decoded_filename.split('.')[-1]}"
                meta_data = decoded_filename[4:].split('.')[0]
            filepath = f"app/{directory}/{filename}"
            async with aiofiles.open(filepath, 'wb') as f:
                contents = await file.read()
                await f.write(contents)
            filenames.append(filepath)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file {file.filename}: {str(e)}")
        finally:
            await file.close()
    return filenames, meta_data

