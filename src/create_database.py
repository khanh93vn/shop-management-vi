import sqlite3 as db
from utils import DATABASE

if __name__ == "__main__":
    # khởi tạo
    conn = db.connect(DATABASE)
    c = conn.cursor()

    try:
        # tạo bảng danh mục hàng
        c.execute("""CREATE TABLE products (
                id INTEGER,
                name TEXT,
                unit TEXT,
                price REAL,
                note TEXT
            )""")

        # tạo bảng danh mục nhà cung cấp
        c.execute("""CREATE TABLE suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                note TEXT
            )""")
        # tạo bảng danh sách khách hàng
        c.execute("""CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                birth_year INTEGER,
                phone TEXT,
                email TEXT,
                note TEXT
            )""")

        # tạo bảng lưu trữ hóa đơn
        c.execute("""CREATE TABLE bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date INTEGER,
                partner_id INTEGER,
                is_selling BOOLEAN,
                batch_count INTEGER,
                note TEXT
            )""")

        # tạo bảng lưu trữ hàng nhập trong hóa đơn
        # mã số hóa đơn tương ứng = mã số lô >> 6 (dịch phải 6 bit)
        c.execute("""CREATE TABLE batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER,
                product_id INTEGER,
                expiration_date INTEGER,
                quantity INTEGER,
                price REAL
            )""")

        # tạo bảng kho (cập nhật liên tục)
        c.execute("""CREATE TABLE stock (
                product_id INTEGER,
                expiration_date INTEGER,
                quantity INTEGER,
                PRIMARY KEY (product_id, expiration_date)
            )""")
    except db.OperationalError as e:
        if "table" in str(e) and "already exists" in str(e):
            print("Database already exists!")
        else:            
            conn.commit()
            conn.close()
            raise e

    # đóng
    conn.commit()
    conn.close()
