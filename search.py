#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\venv\Scripts\Activate
from fastapi.responses import StreamingResponse
from asyncio import sleep
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from fastapi.middleware.cors import CORSMiddleware
from langchain_elasticsearch import ElasticsearchRetriever
from langchain_huggingface import HuggingFaceEmbeddings
import logging
import re
from LLM import GPTHandler
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import csv
import io
import pandas as pd
from tempfile import NamedTemporaryFile
from classSQLs import SQLiteManager
import os
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


LLM = GPTHandler()

# Request model
class QueryRequest(BaseModel):
    query: str

embedding = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")

LLM = GPTHandler()
UPLOAD_DIR = "upload_csv"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Variable to store the uploaded file's data globally
uploaded_data = {"file_path": None, "db_path": None}
# Request model
class QueryRequest(BaseModel):
    query: str

class FileCheckRequest(BaseModel):
    filename: str

# Upload file
@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Uploaded file is not a CSV.")

        # Generate unique file name if the file exists
        base_name, ext = os.path.splitext(file.filename)
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        counter = 1

        while os.path.exists(file_path):
            file_path = os.path.join(UPLOAD_DIR, f"{base_name}({counter}){ext}")
            counter += 1

        # Save the new file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Decode and parse the CSV content
        decoded_content = content.decode("utf-8")
        csv_reader = csv.reader(io.StringIO(decoded_content))

        # Parse CSV into headers and rows
        rows = [row for row in csv_reader]
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty.")

        headers = rows[0]
        data = rows[1:]

        # Define the SQLite database file path
        db_path = os.path.join(UPLOAD_DIR, "database.db")

        # Convert the CSV to SQLite database
        sqlite_manager = SQLiteManager(db_path=db_path)
        result_message = sqlite_manager.csv_to_database(file_path)
        uploaded_data["file_path"] = file_path
        uploaded_data["db_path"] = result_message
        sqlite_manager.close_connection()

        # Return file path along with headers and data
        return {
            # "file_path": file_path,
            "headers": headers,
            "data": data
        }

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Error processing CSV file: {str(e)}"}
        )




@app.post("/get_answer/")
async def get_answer(request: QueryRequest):
    search_query = request.query
    if uploaded_data["file_path"] is None:
        print("no data")
        # return {"message": "no data"}
    else:
        # Lấy tên file từ file_path
        file_path = uploaded_data["file_path"]
        file_name = os.path.basename(file_path)  # Lấy tên file (vd: 'example.csv')
        table_name = os.path.splitext(file_name)[0]  # Loại bỏ đuôi '.csv' (vd: 'example')
        
        # Lấy đường dẫn database
        db_path = uploaded_data["db_path"]

        # Khởi tạo SQLiteManager
        sqlite_manager = SQLiteManager(db_path=db_path)
        
        try:
            # Lấy danh sách cột từ bảng
            columns = sqlite_manager.get_columns(table_name)
                
            sqlite_manager.close_connection()

            print(f"Columns in table '{table_name}': {columns}")

            # Xử lý câu truy vấn với các cột và tên bảng
            sql_script = LLM.process_query(search_query, columns)
            cleaned_output = sql_script.replace("sql", "").replace("```", "").strip()
            print(cleaned_output)

            results = sqlite_manager.execute_query(cleaned_output)
            print(results)

            final_answer = LLM.answerer.answrer_embed(search_query,sql_script,results,4)
            print(final_answer)
            # Trả về kết quả
            return {"results": final_answer}

        except Exception as e:
            sqlite_manager.close_connection()
            print(f"Error: {str(e)}")
            return {"message": f"Error retrieving columns: {str(e)}"}
    # return StreamingResponse(get_answer(), media_type="text/plain")

