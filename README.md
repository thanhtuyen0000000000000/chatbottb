# Chatbot Xử Lý Dữ Liệu Dạng Bảng

## 📝 Mô tả chatbot

Chatbot xử lý dữ liệu dạng bảng là một công cụ được thiết kế nhằm hỗ trợ người dùng tải lên tệp CSV, đặt câu hỏi dựa trên dữ liệu dạng bảng và nhận được câu trả lời một cách chính xác và nhanh chóng. 

## ⚙️ Tính năng chính

- **Tải lên tệp CSV:** Người dùng có thể dễ dàng tải tệp CSV lên hệ thống.
- **Xử lý câu hỏi:** Chatbot phân tích câu hỏi của người dùng và tìm kiếm câu trả lời trong dữ liệu.
- **Đưa ra câu trả lời:** Dựa trên nội dung trong tệp CSV, chatbot sẽ cung cấp câu trả lời phù hợp.
- **Hỗ trợ ngôn ngữ tự nhiên:** Người dùng có thể đặt câu hỏi bằng ngôn ngữ tự nhiên mà không cần cấu trúc đặc biệt.

## 🛠️ Công nghệ sử dụng

- **Ngôn ngữ lập trình:** Python
- **Thư viện:**
  - Pandas: Xử lý dữ liệu CSV.
  - OpenAI API: Hiểu và phân tích câu hỏi ngôn ngữ tự nhiên.
  - Reactjs/FastAPI: Xây dựng giao diện API.

## 🚀 Cách sử dụng

### 1. Cài đặt yêu cầu

Cài đặt các thư viện cần thiết bằng cách sử dụng `pip`:

```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

Khởi động ứng dụng bằng lệnh:

```bash
uvicorn search:app --reload
```

```bash
cd frontend
npm run dev 
```

### 3. Tương tác với chatbot

1. Truy cập giao diện web tại `http://localhost:5173`.
2. Tải lên tệp CSV.
3. Nhập câu hỏi của bạn vào ô chat và nhận câu trả lời từ chatbot.
