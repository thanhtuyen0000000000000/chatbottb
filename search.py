#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\.venv\Scripts\Activate
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from chatbot_tabular.chatbot_tabular.classSQLs import SQLiteManager

from chatbot_tabular.chatbot_tabular.LLM import GPTHandler

import csv
import io
import os
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LLM = GPTHandler()

uri = "mongodb+srv://thungaho0106:ZUBvDg7FhyxpxKd4@qaotd.f7fya.mongodb.net/?retryWrites=true&w=majority&ssl=true"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["QAoTD"]
questions_collection = db["questions"]
answers_collection = db["answers"]
files_collection = db["files"]

# Request model
class QueryRequest(BaseModel):
    query: str


LLM = GPTHandler()
UPLOAD_DIR = "upload_csv"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Variable to store the uploaded file's data globally
uploaded_data = {"file_path": None, "db_path": None}
# Request model
class QueryRequest(BaseModel):
    query: str
    session_id: str 

class FileCheckRequest(BaseModel):
    filename: str

# Upload file
@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...),session_id: str = Form(None)):
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


        # Lưu đường dẫn tệp và session_id vào collection `files`
        file_data = {
            "session_id": session_id,
            "file_path": file_path,
            "filename": file.filename,
            "timestamp": datetime.utcnow().isoformat()
        }

        files_collection.insert_one(file_data)

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

@app.get("/get_sessions/")
async def get_sessions():
    try:
        sessions = list(files_collection.find({}, {"_id": 0, "session_id": 1}))
        return {"sessions": sessions}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error retrieving sessions: {str(e)}"})
    

@app.get("/get_session_data/{session_id}/")
async def get_session_data(session_id: str):
    try:
        # Lấy các câu hỏi theo session_id
        questions = list(questions_collection.find({"session_id": session_id}))
        answers = list(answers_collection.find({"session_id": session_id}))

        # Chuyển dữ liệu sang định dạng frontend-friendly
        session_data = []
        for question, answer in zip(questions, answers):
            session_data.append({
                "query": question["query"],
                "answer": answer["answer"],
                "timestamp": question["timestamp"]
            })

        file_data = files_collection.find_one({"session_id": session_id})
        print("Adfdf", file_data)
        if file_data:
            print(0)
            # Lấy file cuối cùng
            file_path = file_data["file_path"]
            print(2)
            filename = file_data["filename"]
            print(3)

            # Đọc nội dung file nếu cần
            with open(file_path, "r", encoding="utf-8") as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
                headers = rows[0] if rows else []
                data = rows[1:] if len(rows) > 1 else []
        else:
            filename, headers, data = None, [], []

        return {
            "session_id": session_id,
            "data": session_data,
            "file_info": {
                "filename": filename,
                "headers": headers,
                "data": data
            }
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error retrieving session data: {str(e)}"})

@app.get("/get_unique_file_paths/{session_id}/")
async def get_unique_file_paths(session_id: str):
    try:
        # Lấy các file theo session_id
        file_records = list(files_collection.find({"session_id": session_id}, {"_id": 0, "file_path": 1}))

        # Lưu các file paths vào một danh sách và loại bỏ trùng lặp
        unique_file_paths = list({file["file_path"] for file in file_records})
        print(unique_file_paths)
        return {
            "session_id": session_id,
            "unique_file_paths": unique_file_paths
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error retrieving unique file paths: {str(e)}"})

@app.get("/get_all_file_paths/")
async def get_all_file_paths():
    try:
        # Lấy toàn bộ file records từ database
        file_records = list(files_collection.find({}, {"_id": 0, "file_path": 1, "filename": 1}))

        # Trích xuất unique file paths và filenames
        unique_files = [
            {"file_path": file["file_path"], "filename": file["filename"]}
            for file in file_records
        ]
        print(unique_files)
        return {"files": unique_files}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Error retrieving file paths: {str(e)}"}
        )

@app.get("/get_file_content/")
async def get_file_content(file_path: str):
    try:
        # Đọc nội dung file CSV
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {"file_path": file_path, "file_content": content}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Error retrieving file content: {str(e)}"}
        )

@app.post("/get_answer/")
async def get_answer(request: QueryRequest):
    search_query = request.query
    session_id = request.session_id
    cleaned_output = None
    results = None
    if uploaded_data["file_path"] is None:
        print("no data")
        category = LLM.classifier.classify_small_talk(search_query)
        print(category)
        if (category =="Small Talk"):
            final_answer = LLM.answerer.answer_smalltalk(search_query,2)
        elif (category == "Not English"):
            final_answer = "Sorry I only support English language"
        else:
            final_answer = "Sorry I don't know"
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
            category = LLM.classifier.classify_column_related(search_query,columns)
            print("-----------------",category)
            if (category =="Small Talk"):
                final_answer = LLM.answerer.answer_smalltalk(search_query,2)
            elif (category == "Unrelated to Table"):
                final_answer = "The question is unrelate to table data"
            elif (category == "Not English"):
                final_answer = "Sorry I only support English language"
            else:
            # Xử lý câu truy vấn với các cột và tên bảng
                sql_script = LLM.process_query(search_query, columns)
                cleaned_output = sql_script.replace("sql", "").replace("```", "").strip()
                print(cleaned_output)

                results = sqlite_manager.execute_query(cleaned_output)
                print(results)

                final_answer = LLM.answerer.answrer_embed(search_query,sql_script,results,4)
                print(final_answer)
        except Exception as e:
            sqlite_manager.close_connection()
            print(f"Error: {str(e)}")
            return {"message": f"Error retrieving columns: {str(e)}"}
    # return StreamingResponse(get_answer(), media_type="text/plain")

    timestamp = datetime.utcnow().isoformat()

    # Lưu câu hỏi vào collection `questions`
    question_data = {
        "session_id": session_id,
        "query": search_query,
        "timestamp": timestamp
    }
    question_id = questions_collection.insert_one(question_data).inserted_id

    # Lưu câu trả lời vào collection `answers`
    answer_data = {
        "session_id": session_id,
        "question_id": str(question_id),
        "sql_script": cleaned_output,
        "result": results,
        "answer": final_answer,
        "timestamp": timestamp
    }
    answers_collection.insert_one(answer_data)

    return {"results": final_answer}

        
