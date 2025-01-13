#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\.venv\Scripts\Activate
from fastapi import FastAPI, HTTPException
from fastapi import Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from LLM import GPTHandler
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import csv
import io
from classSQLs import SQLiteManager
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối MongoDB
uri = "mongodb+srv://thungaho0106:ZUBvDg7FhyxpxKd4@qaotd.f7fya.mongodb.net/?retryWrites=true&w=majority&ssl=true"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["QAoTD"]
questions_collection = db["questions"]
answers_collection = db["answers"]
files_collection = db["files"]

LLM = GPTHandler()

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
async def upload_csv(file: UploadFile = File(...), session_id: str = Form(None)):
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Uploaded file is not a CSV.")

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        if os.path.exists(file_path):
            os.remove(file_path)

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

        # Store the file path globally
        uploaded_data["file_path"] = file_path

        # Define the SQLite database file path
        db_path = os.path.join(UPLOAD_DIR, "database.db")

        # Convert the CSV to SQLite database
        sqlite_manager = SQLiteManager(db_path=db_path)
        result_message = sqlite_manager.csv_to_database(file_path)
        sqlite_manager.close_connection()

        # Store the SQLite database path globally
        uploaded_data["db_path"] = result_message

        # Lưu đường dẫn tệp và session_id vào collection `files`
        file_data = {
            "session_id": session_id,
            "file_path": file_path,
            "filename": file.filename,
            "timestamp": datetime.utcnow().isoformat()
        }

        files_collection.insert_one(file_data)

        return {"headers": headers, "data": data}

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
    
# retrieve_keyword = retrieval_keyword()
# retrieve_embedding= retrieval_embedding()
# FastAPI route to get an answer from Elasticsearch

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

@app.post("/get_answer/")
async def get_answer(request: QueryRequest):
    search_query = request.query
    session_id = request.session_id

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

# Tạo session_id và timestamp

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

        except Exception as e:
            sqlite_manager.close_connection()
            print(f"Error: {str(e)}")
            return {"message": f"Error retrieving columns: {str(e)}"}
    # return StreamingResponse(get_answer(), media_type="text/plain")

