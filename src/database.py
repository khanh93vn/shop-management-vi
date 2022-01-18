"""
Credit: Henrique Miranda, posted in
https://stackoverflow.com/questions/50381616/how-to-connect-to-a-protected-sqlite3-database-with-python
"""

import sys
from pysqlcipher3 import dbapi2 as sqlite3
from utils import DATABASE_PATH, DATABASE_PRAGMA_KEY


class Database(object):
    table_names_query = "SELECT name FROM sqlite_master WHERE type='table'"
    def __init__(self, dbname):
        self.dbname = dbname

    def connDB(self):
        self.conn = sqlite3.connect(self.dbname)
        self.cursor = self.conn.cursor()
        self.cursor.execute(DATABASE_PRAGMA_KEY)

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

    def queryDB(self, sql, *args, commit=True):
        self.connDB()
        
        try:
            self.cursor.execute(sql, *args)

            if sql[0:6].lower() == 'select':
                result = self.cursor.fetchall()
                self.conn.close()
                return result
            else:
                if commit:
                    self.conn.commit()
                    self.conn.close()
        
        except Exception as e:
            self.conn.close()
            raise e
    
    def closeDB(self, commit=True):
        if commit:
            self.conn.commit()
        self.conn.close()
    
    def list_tables(self):
        return next(zip(*self.queryDB(self.table_names_query)))
    
    def get_last_item(self, table):
        return queryDB('SELECT seq FROM sqlite_sequence WHERE name = "{table}"')


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

    def get_names_from_table(self, table, pattern='%'):
        fetched = self.queryDB(f"SELECT name FROM {table} WHERE name like ? ORDER BY name", (pattern,))
        
        return [name for name, in fetched]
    
    def insert_if_not_exists(self, table, searchby,
                             valuesdict, commit=False):
        # xây dựng chuỗi truy vấn
        if isinstance(searchby, str):
            searchby = searchby,
        placeholder = ','.join(['?']*len(searchby))
        searchvalues = tuple(valuesdict[k] for k in searchby)
        searchby = ','.join(searchby)
        query = "SELECT * FROM {} WHERE ({}) = ({})".format(table, searchby, placeholder)
        
        data = self.queryDB(query, searchvalues)
        if len(data) > 1:
            raise ValueError(f"duplicate {table}")
        elif len(data) == 1:
            return data[0]
        else:
            self.queryDB(f"""INSERT INTO {table} ({','.join(valuesdict)})
                                VALUES ({','.join(['?']*len(valuesdict))})""",
                            tuple(valuesdict.values()),
                            commit=commit)
            return self.queryDB(query, searchvalues)
            
if __name__ == "__main__":
    if len(sys.argv[1]) > 1:
        if(sys.argv[1]) == "create":    # khởi tạo
            db = MedStoreDatabase(DATABASE_PATH)
            db.createDB()
        