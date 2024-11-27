import aiofiles
from fastapi import UploadFile, HTTPException
from typing import List


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
    for file in files:
        try:
            filename = f"{file.filename.split('.')[0][17:21]}.{file.filename.split('.')[-1]}"
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

