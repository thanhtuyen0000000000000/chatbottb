import pandas as pd
import sqlite3
import os
import re

class SQLiteManager:
    def __init__(self, db_path='database.db'):
        """
        Khởi tạo SQLiteManager với đường dẫn đến database SQLite.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def map_dtype(self, dtype):
        """
        Ánh xạ kiểu dữ liệu của pandas sang kiểu dữ liệu SQLite.
        """
        if pd.api.types.is_string_dtype(dtype):
            return "TEXT COLLATE NOCASE"
        elif pd.api.types.is_numeric_dtype(dtype):
            return "REAL"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "DATETIME"
        else:
            return "TEXT"

    def sanitize_column_name(self, col_name):
        """
        Chuẩn hóa tên cột để phù hợp với SQLite.
        """
        return re.sub(r'[^\w]', '_', col_name)

    def handle_duplicate_columns(self, df):
        """
        Loại bỏ các cột trùng lặp trong DataFrame.
        """
        seen_columns = {}
        duplicates = []
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in seen_columns:
                duplicates.append(col)
            else:
                seen_columns[col_lower] = col
        df = df.drop(columns=duplicates)
        return df

    def csv_to_database(self, csv_path, chunksize=500):
        """
        Chuyển file CSV thành bảng trong SQLite database.
        """
        file_name = os.path.basename(csv_path)
        table_name = os.path.splitext(file_name)[0]
        table_name = f"[{table_name}]"

        # Đọc dữ liệu từ file CSV
        data = pd.read_csv(csv_path)
        data = self.handle_duplicate_columns(data)
        data.columns = [self.sanitize_column_name(col) for col in data.columns]

        # Tạo câu lệnh CREATE TABLE
        columns = ", ".join(
            f"[{col}] {self.map_dtype(dtype)}" for col, dtype in zip(data.columns, data.dtypes)
        )

        # Kiểm tra và xóa bảng cũ nếu bảng đã tồn tại
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns}
        );
        """
        self.cursor.execute(create_table_query)

        # Thêm dữ liệu vào bảng
        for chunk in range(0, len(data), chunksize):
            data_chunk = data.iloc[chunk: chunk + chunksize]
            data_chunk.to_sql(table_name.strip('[]'), self.conn, if_exists='append', index=False)
        print(f"File CSV '{file_name}' đã được chuyển đổi thành bảng '{table_name}' trong database.")
        # return f"File CSV '{file_name}' đã được chuyển đổi thành bảng '{table_name}' trong database."
        return self.db_path

    def get_columns(self, table_name):
        try:    
            # Thực hiện truy vấn để lấy thông tin các cột
            self.cursor.execute(f"PRAGMA table_info([{table_name}]);")
            columns = self.cursor.fetchall()

            if not columns:
                return f"Bảng '{table_name}' không tồn tại hoặc không có cột nào."
            
            # Trả về thông tin cột dưới dạng danh sách tuple (column_name, column_type)
            column_info = [{"column_name": column[1], "column_type": column[2],"table_name": table_name} for column in columns]
            return column_info
        
        except sqlite3.Error as e:
            return f"Lỗi khi truy cập cơ sở dữ liệu: {e}"


    def execute_query(self, query):
        
        try:
            conn = sqlite3.connect(self.db_path)  # Kết nối cơ sở dữ liệu
            cursor = conn.cursor()  # Tạo con trỏ
            cursor.execute(query)  # Thực thi truy vấn
            result = cursor.fetchall()  # Lấy kết quả truy vấn
            conn.close()  # Đóng kết nối
            if not result:
                return "No data."
            return result
        except sqlite3.Error as e:
            return f"Lỗi khi thực thi truy vấn: {e}"

        # self.cursor.execute(query)
        # if query.strip().lower().startswith("select"):
        #     return self.cursor.fetchall()
        # self.conn.commit()
        # return f"Truy vấn SQL thực hiện thành công."

    def close_connection(self):
        """
        Đóng kết nối với SQLite database.
        """
        self.conn.close()
