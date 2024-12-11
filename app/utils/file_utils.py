import zipfile
import aiofiles
from fastapi import UploadFile, HTTPException
from typing import List
from urllib.parse import unquote
import os

# async def main_save_uploaded_files(files: List[UploadFile], directory: str, index: int = 0) -> List[str]:
#     filenames = []
#     for file in files:
#         try:
#             filename = f"{file.filename.split('.')[0]}{index}.{file.filename.split('.')[-1]}"
#             filepath = f"app/{directory}/{filename}"
#             async with aiofiles.open(filepath, 'wb') as f:
#                 contents = await file.read()
#                 await f.write(contents)
#             filenames.append(filepath)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Error saving file {file.filename}: {str(e)}")
#         finally:
#             await file.close()
#     return filenames

async def extract_zip_with_index(zip_path, extract_to, main_file_index):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            # Извлечение имени файла и расширения
            filename, file_extension = os.path.splitext(file_info.filename)

            # Создание нового имени файла с добавлением main_file_index перед расширением
            new_filename = f"{filename[:4]}{main_file_index}{file_extension}"
            extracted_path = os.path.join(extract_to, new_filename)

            # Извлечение файла с новым именем
            with zip_ref.open(file_info.filename) as source_file:
                with open(extracted_path, 'wb') as target_file:
                    target_file.write(source_file.read())
            
            print(f"Extracted file to {extracted_path}")

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

