"""import sqlite3  as db


# kết nối với CSDL
conn = db.connect("data.db")
c = conn.cursor()

# c.execute('SELECT seq FROM sqlite_sequence WHERE name = "bills"')
c.execute('SELECT name FROM products')
print([item for item, in c.fetchall()])

# ngắt kết nối với CSDL
conn.commit()
conn.close()
"""

a, *b, c = range(5)

print(a, b, c)