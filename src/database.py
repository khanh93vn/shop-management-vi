"""
Credit: Henrique Miranda, posted in
https://stackoverflow.com/questions/50381616/how-to-connect-to-a-protected-sqlite3-database-with-python
"""

import sys
from pysqlcipher3 import dbapi2 as sqlite3
if __name__ == "__main__":
    from utils import DATABASE_PATH
else:
    from .utils import DATABASE_PATH


class Database(object):
    table_names_query = "SELECT name FROM sqlite_master WHERE type='table'"
    def __init__(self, dbname):
        self.dbname = dbname

    def connDB(self):
        self.conn = sqlite3.connect(self.dbname)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA key='WzW7cVMm30453118'")

    def createDB(self):
        self.connDB()
        try:
            self.cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                login TEXT NOT NULL,
                passwd TEXT);
                '''
            )

            self.cursor.execute(
                '''
                INSERT INTO users (name, login, passwd)
                VALUES ("Admininstrator", "admin", "12345")
                '''
            )
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            self.conn.close()
            raise e

    def queryDB(self, sql):
        self.connDB()
        
        try:
            self.cursor.execute(sql)

            if sql[0:6].lower() == 'select':
                result = self.cursor.fetchall()
                self.conn.close()
                return result
            else:
                self.conn.commit()
                self.conn.close()
        
        except Exception as e:
            self.conn.close()
            raise e
    
    def list_tables(self):
        return next(zip(*self.queryDB(self.table_names_query)))


class MedStoreDatabase(Database):
    def createDB(self):
        try:
            super().createDB()
            # tạo bảng danh mục hàng
            self.queryDB("""CREATE TABLE products (
                    id INTEGER,
                    name TEXT,
                    unit TEXT,
                    price REAL,
                    note TEXT
                )""")

            # tạo bảng danh mục nhà cung cấp
            self.queryDB("""CREATE TABLE suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    note TEXT
                )""")
            # tạo bảng danh sách khách hàng
            self.queryDB("""CREATE TABLE customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    birth_year INTEGER,
                    phone TEXT,
                    email TEXT,
                    note TEXT
                )""")

            # tạo bảng lưu trữ hóa đơn
            self.queryDB("""CREATE TABLE bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date INTEGER,
                    partner_id INTEGER,
                    is_selling BOOLEAN,
                    batch_count INTEGER,
                    note TEXT
                )""")

            # tạo bảng lưu trữ hàng nhập trong hóa đơn
            # mã số hóa đơn tương ứng = mã số lô >> 6 (dịch phải 6 bit)
            self.queryDB("""CREATE TABLE batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER,
                    product_id INTEGER,
                    expiration_date INTEGER,
                    quantity INTEGER,
                    price REAL
                )""")

            # tạo bảng kho (cập nhật liên tục)
            self.queryDB("""CREATE TABLE stock (
                    product_id INTEGER,
                    expiration_date INTEGER,
                    quantity INTEGER,
                    PRIMARY KEY (product_id, expiration_date)
                )""")
            
        except sqlite3.OperationalError as e:
            if "table" in str(e) and "already exists" in str(e):
                print("Database already exists!")
            else:
                raise e
            
if __name__ == "__main__":
    if len(sys.argv[1]) > 1:
        if(sys.argv[1]) == "create":    # khởi tạo
            db = MedStoreDatabase(DATABASE_PATH)
            db.createDB()
        # elif 