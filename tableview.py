import tkinter as tk
import tkinter.ttk as ttk
import sqlite3 as db

from form import Form, Date, Textbox
from utils import *

class ProductViewTab(ttk.Frame):
    table_name = "products"
    sort_key = "name"
    primary_keys = ("id",)
    class ViewForm(Form):
        frame_name = "Thông tin"
        fields = [
            # name, description, type, unit
            ("id", "Mã số", tk.StringVar, None),
            ("name", "Tên", tk.StringVar, None),
            ("unit", "Đơn vị tính", (tk.StringVar, item_units), None),
            ("price", "Đơn giá bán", tk.DoubleVar, None),
            ("note", "Ghi chú", Textbox, None),
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # form điền thông tin
        self.form = self.ViewForm(self)
        self.form.place(relx=0.01, rely=0.01, relwidth=0.48, relheight=0.88)
        
        # ô xem dữ liệu ở bên phải
        self.item_view = ItemView(self)
        self.item_view.place(relx=0.51, rely=0.01, relwidth=0.48, relheight=0.98)
        self.item_view.init_columns([desc for _, desc, *_ in self.ViewForm.fields])
        self.reload_data()
        
        # nút cập nhật (chỉnh sửa) hàng
        self.update_button = tk.Button(self, command=self.update_item, text="Cập nhật (chỉnh sửa)", font=DEFAULT_FONT)
        self.update_button.place(relx=0.01, rely=0.89, relheight=0.09, relwidth=0.24)
        
        # nút cập nhật dữ liệu
        self.update_button = tk.Button(self, command=self.reload_data, text="Làm mới", font=DEFAULT_FONT)
        self.update_button.place(relx=0.25, rely=0.89, relheight=0.09, relwidth=0.24)
    
    def update_item(self):
        # lấy dữ liệu từ form
        data = {key:value for value, (key, *_) in zip(self.form.get_data(), self.ViewForm.fields)}
        fields = ','.join(data)
        place_holders = ','.join(['?']*len(self.ViewForm.fields))
        primary_keys = ','.join(self.primary_keys)
        
        # cập nhật mẫu dữ liệu
        conn = db.connect(DATABASE)
        c = conn.cursor()
        query_values = (*data.values(), *(data[key] for key in self.primary_keys))
        c.execute(f"""UPDATE {self.table_name}
                      SET ({fields}) = ({place_holders})
                      WHERE ({primary_keys}) = (?)""",
                  query_values)
        conn.commit()
        conn.close()
        
        # làm mới ô xem
        self.reload_data()
    
    def edit_item(self):
        values = next(self.item_view.get_selected())    # lấy dòng đầu tiên được chọn
        self.form.set_data(values)
    
    def reload_data(self):
        # kết nối với CSDL
        conn = db.connect(DATABASE)
        c = conn.cursor()

        c.execute(f"SELECT * FROM {self.table_name} ORDER BY {self.sort_key}")
        data = c.fetchall()

        # ngắt kết nối với CSDL
        conn.close()
        
        self.item_view.clear_items()
        self.item_view.add_items(data)
    
    def _init_form(self):
        pass
    
    def _init_view(self):
        pass

class ItemView(ttk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, text="Dữ liệu",**kwargs)
        container = args[0]
        
        self.columnconfigure(0, weight=20)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=50)
        self.rowconfigure(1, weight=1)
        
        # bảng xem dữ liệu
        self.table = ttk.Treeview(self, show='headings')
        self.table.grid(row=0, column=0,
                        padx=relativeW(3),
                        pady=relativeH(3),
                        sticky="nwes")
        
        # con lăn dọc
        self.scrollbarV = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.scrollbarV.grid(row=0, column=1, sticky="nws")
        self.table.configure(xscrollcommand=self.scrollbarV.set)
        
        # con lăn ngang
        self.scrollbarH = ttk.Scrollbar(self, orient="horizontal", command=self.table.xview)
        self.scrollbarH.grid(row=1, column=0, sticky="nwe")
        self.table.configure(xscrollcommand=self.scrollbarH.set)
        
        # callback khi double-click
        self.table.bind("<Double-1>", lambda event: container.edit_item())

    def init_columns(self, columns):
        self.table["columns"] = tuple(range(len(columns)))
        w = relativeW(70)//len(columns)
        for i, column in enumerate(columns):
            self.table.column(i, width=w, anchor ='se')
            self.table.heading(i, text=column)
    
    def add_items(self, items):
        for item in items:
            self.table.insert("", 'end', values=item)
    
    def replace_item(self, item):
        index = self.table.selection()[0]
        self.table.delete(index)
        self.table.insert("", int(index[1:]) - 1, values=item)
    
    def delete_item(self):
        indices = self.table.selection()
        for index in indices:
            self.table.delete(item)
    
    def clear_items(self):
        for index in self.table.get_children():
            self.table.delete(index)
    
    def get_selected(self):
        for index in self.table.selection():
            yield self.table.item(index)["values"]
    
    def get_data(self):
        for index in self.table.get_children():
            yield self.table.item(index)["values"]

