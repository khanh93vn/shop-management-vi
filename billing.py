"""
Handle stock import export interfaces and workings.

BaseBillingTab: base object for billing operations (selling and buying)
"""

import tkinter as tk
import sqlite3 as db
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox

from form import Textbox, Date, Form
from utils import *

# màn hình chính của tab (base)
class BaseBillingTab(ttk.Frame):
    InfoForm = None                 # set = frame InfoForm class tự tạo
    is_buying = None                # set = True hoặc False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # frame thêm sản phẩm ở góc trên bên trái
        self.add_item_form = AddItemForm(self)
        self.add_item_form.place(relx=0.01, rely=0.01, relwidth=0.48, relheight=0.40)
        
        # frame điền thông tin đơn hàng ở góc dưới bên trái
        self.info_form = self.InfoForm(self)
        self.info_form.place(relx=0.01, rely=0.42, relwidth=0.48, relheight=0.57)
        self.partner_info_keys = [field[0] for field in self.info_form.fields[1:-1]]
        
        # ô xem các sản phẩm đã thêm ở bên phải
        self.item_view = ItemView(self)
        self.item_view.place(relx=0.51, rely=0.01, relwidth=0.48, relheight=0.88)
        
        # nút nhập hàng
        self.checkout_button = tk.Button(self, command=self.checkout, text="Thanh toán", font=DEFAULT_FONT)
        self.checkout_button.place(relx=0.51, rely=0.89, relheight=0.09, relwidth=0.48)
        
        # Tạo danh sách tên nhà cung cấp/khách hàng và gắn callback cho mục tự động điền thông tin
        self.update_partners()
        self.bind_partner_autofill_callback()
        
        # Tạo danh sách tên sản phẩm và gắn callback cho mục tự động điền thông tin sản phẩm
        self.update_products()
        self.bind_product_autofill_callback()
        
    
    def product_check(self):
        # lấy dữ liệu từ form
        product_id, product_name, unit, price, quantity, exp_date, discount, vat = self.add_item_form.get_data()
        
        # kiểm tra thông tin
        if not (product_id and product_name and unit):
            messagebox.showinfo("Thiếu thông tin", "Xin điền thông tin!")
            return
        
        if price <= 0 or quantity <= 0:
            messagebox.showinfo("Thông tin sai", "Đơn giá và số lượng phải lớn hơn 0")
            return
        
        # kết nối với CSDL
        conn = db.connect(DATABASE)
        c = conn.cursor()
            
        # kiểm tra xem sản phẩm đã có trong danh mục chưa
        ret = create_if_not_exists(c, table="products", searchby="id",
                                   valuesdict={"id": product_id, "name": product_name, "unit": unit},
                                   prompt=("Sản phẩm", "Thêm sản phẩm"))
        if ret is not None:
            product_id, product_name, unit, _, note = ret
            self.update_products()
        else:
            # ngắt kết nối với CSDL trước khi thoát
            conn.close()
            return

        conn.commit()
        conn.close()
        return (product_id, product_name, unit, price, quantity, exp_date, discount, vat)
    
    def partner_check(self, cursor, partner_info):
        raise NotImplementedError
    
    def checkout(self):
        # lấy dữ liệu hóa đơn
        date, *partner_info, note = self.info_form.get_data()
        timestamp = datestr2int(date)
        
        # kiểm tra thông tin
        if not date:
            messagebox.showinfo("Thiếu thông tin", "Xin điền thông tin!")
            return
        
        # kết nối với CSDL
        conn = db.connect(DATABASE)
        c = conn.cursor()
        
        # kiểm tra ô tên nhà cung cấp/khách hàng
        ret = self.partner_check(c, partner_info)
        if ret is not None:
            partner_id, *_ = ret
            self.update_partners()
        else:
            # ngắt kết nối với CSDL trước khi thoát
            conn.close()
            return
        
        batches = [*self.item_view.get_data()]
        # nhập hóa đơn
        c.execute("INSERT INTO bills (date, partner_id, is_selling, batch_count, note) VALUES (?, ?, ?, ?, ?)",
                  (timestamp, partner_id, self.is_selling, len(batches), note))
        
        # lấy lại mã số hóa đơn vừa nhập
        c.execute('SELECT seq FROM sqlite_sequence WHERE name = "bills"')
        bill_id = c.fetchone()[0]
        # nhập các mặt hàng có trong hóa đơn
        for product_id, product_name, unit, price, quantity, exp_date, discount, vat in batches:
            # cập nhật giá
            price = price*(1 - discount*.01)*(1.1 if vat else 1.0)
            
            # cập nhật hạn sử dụng (quy ước 0 cho sản phẩm không có hạn sử dụng hoặc đã quá hạn sử dụng)
            exp_ts = datestr2int(exp_date)
            if exp_ts <= datestr2int(today()):
                exp_ts = 0
                
            c.execute("""INSERT INTO batches (bill_id, product_id, expiration_date, quantity, price)
                         VALUES (?, ?, ?, ?, ?)""",
                      (bill_id, product_id, exp_ts, quantity, price))
        
            # Cập nhật kho hàng
            ret = create_if_not_exists(c, table="stock", searchby=("product_id", "expiration_date"),
                                       valuesdict={"product_id": product_id,
                                                   "expiration_date": exp_ts,
                                                   "quantity": 0})
            if ret is None:
                raise SystemError("lỗi đọc dữ liệu kho hàng")
            product_id, expiration_date, stock = ret
            
            if not self.is_selling:
                new_stock = stock + quantity
            else:
                new_stock = stock - quantity
                if new_stock < 0:
                    conn.close()
                    raise ValueError("out of stock")
                
            
            # cập nhật dữ liệu
            c.execute("""UPDATE stock SET quantity = (?)
                         WHERE (product_id, expiration_date) = (?, ?)""",
                      (new_stock, product_id, exp_ts))
        
        # lưu lại nếu không có vấn đề
        conn.commit()
        
        # ngắt kết nối với CSDL
        conn.close()
        
        # Thông báo cho người dùng
        messagebox.showinfo("Thành công", "Lưu hóa đơn thành công!")
        
        # xóa danh sách hàng hiện tại
        self.item_view.clear_items()
        
        self.update_products()
        
    def add_item(self):
        ret = self.product_check()
        if ret is not None:
            self.item_view.add_item(ret)
    
    def replace_item(self):
        ret = self.product_check()
        if ret is not None:
            self.item_view.replace_item(ret)
    
    def update_partners(self):
        raise NotImplementedError
    
    def update_products(self):
        product_names = get_names_from_table("products")
        self.add_item_form.nameE["values"] = product_names
    
    def bind_partner_autofill_callback(self):
        raise NotImplementedError
    
    def bind_product_autofill_callback(self):
        def callback_fill_product(key, var):
            # kết nối với CSDL
            conn = db.connect(DATABASE)
            c = conn.cursor()
            c.execute(f"SELECT * FROM products WHERE {key} = (?)", (var.get(),))
            try:
                product_id, product_name, unit, price, note = c.fetchone()
                self.add_item_form.id.set(product_id)
                self.add_item_form.name.set(product_name)
                self.add_item_form.unit.set(unit)
            except TypeError as e:
                if "NoneType object" not in str(e):
                    raise e
            conn.close()
        self.add_item_form.id.trace_add("write", lambda var, index, mode: callback_fill_product("id", self.add_item_form.id))
        self.add_item_form.nameE.bind("<<ComboboxSelected>>",
                                      lambda event: callback_fill_product("name", self.add_item_form.name))


# frame thông tin đơn hàng (bán)
class BuyingInfoForm(Form):
    frame_name = "Thông tin đơn hàng"
    fields = [
        # name, description, type, unit
        ("date", "Ngày hóa đơn", Date, None),
        ("provider", "Nhà cung cấp", (tk.StringVar, []), None),
        ("phone", "Số điện thoại", tk.StringVar, None),
        ("note", "Ghi chú đơn hàng", Textbox, None),
    ]

# frame thông tin đơn hàng (mua)
class SellingInfoForm(Form):
    frame_name = "Thông tin đơn hàng"
    fields = [
        # name, description, type, unit
        ("date", "Ngày hóa đơn", Date, None),
        ("customer", "Khách hàng", (tk.StringVar, []), None),
        ("age", "Tuổi", tk.IntVar, None),
        ("phone", "Số điện thoại", tk.StringVar, None),
        ("email", "E-mail", tk.StringVar, None),
        ("note", "Ghi chú đơn hàng", Textbox, None),
    ]

# frame thêm sản phẩm
class AddItemForm(Form):
    frame_name = "Thêm mặt hàng"
    fields = [
        # name, description, type, unit
        ("id", "Mã hàng", tk.StringVar, None),                      # Mã mặt hàng
        ("name", "Tên mặt hàng", (tk.StringVar, []), None),         # Tên mặt hàng
        ("unit", "Đơn vị tính", (tk.StringVar, item_units), None),   # Đơn vị tính
        ("price", "Đơn giá", tk.DoubleVar, "đồng"),                 # Đơn giá
        ("quantity", "Số lượng", tk.IntVar, "$unit"),               # Số lượng
        ("expiration_date", "Hạn sử dụng", Date, None),             # Hạn sử dụng
        ("discount", "Chiết khấu", tk.DoubleVar, "%"),              # Chiết khấu
        ("vat", "Tính thuế VAT", tk.BooleanVar, None),              # VAT
    ]


class ItemView(ttk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, text="Hóa đơn",**kwargs)
        container = args[0]
        
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=5)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=48)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)
        self.rowconfigure(3, weight=3)
        
        # bảng xem dữ liệu
        self.table = ttk.Treeview(self, show='headings')
        self.table.grid(row=0, column=0,
                        padx=relativeW(3),
                        pady=relativeH(3),
                        columnspan=3,
                        sticky="nwes")
        
        # con lăn dọc
        self.scrollbarV = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.scrollbarV.grid(row=0, column=3, sticky="nws")
        self.table.configure(xscrollcommand=self.scrollbarV.set)
        
        # con lăn ngang
        self.scrollbarH = ttk.Scrollbar(self, orient="horizontal", command=self.table.xview)
        self.scrollbarH.grid(row=1, column=0, columnspan=3, sticky="nwe")
        self.table.configure(xscrollcommand=self.scrollbarH.set)
        
        # các cột
        self.table["columns"] = tuple(range(len(AddItemForm.fields)))
        w = relativeW(70)//len(AddItemForm.fields)
        for i, (_, desc, *_) in enumerate(AddItemForm.fields):
            self.table.column(i, width=w, anchor ='se') # 'se'
            self.table.heading(i, text=desc)
        
        # Tổng giá trị đơn hàng
        self.total = tk.StringVar()
        self.totalL = tk.Label(self, text="Tổng :", anchor=tk.W, font=DEFAULT_FONT)
        self.totalL.grid(row=2, column=0, columnspan=1, sticky='nwse')
        self.totalV = tk.Label(self, textvariable=self.total, anchor=tk.E, font=DEFAULT_FONT)
        self.totalV.grid(row=2, column=1, columnspan=1, sticky='nwse')
        self.recompute_total()
        
        # nút thêm mới
        self.add_item_button = tk.Button(self, command=container.add_item, text="Thêm mới", font=DEFAULT_FONT)
        self.add_item_button.grid(row=3, column=0, sticky="nwes")
        
        # nút thay thế
        self.replace_item_button = tk.Button(self, command=container.replace_item, text="Sửa", font=DEFAULT_FONT)
        self.replace_item_button.grid(row=3, column=1, sticky="nwes")
        
        # nút xóa
        self.delete_item_button = tk.Button(self, command=self.delete_item, text="Xóa", font=DEFAULT_FONT)
        self.delete_item_button.grid(row=3, column=2, sticky="nwes")
        
    
    def add_item(self, newItem):
        self.table.insert("", 'end', values=newItem)
        self.recompute_total()
    
    def replace_item(self, newItem):
        item = self.table.selection()[0]
        self.table.delete(item)
        self.table.insert("", int(item[1:]) - 1, values=newItem)
        self.recompute_total()
    
    def delete_item(self):
        selected = self.table.selection()
        for item in selected:
            self.table.delete(item)
        self.recompute_total()
    
    def clear_items(self):
        for child in self.table.get_children():
            self.table.delete(child)
    
    def get_data(self):
        for child in self.table.get_children():
            item_values = self.table.item(child)["values"]
            yield tuple(dataconv(typ)(s) for s, (_, _, typ, *_) in zip(item_values, AddItemForm.fields))
            
    def recompute_total(self):
        total = 0
        for product_id, product_name, unit, price, quantity, exp_date, discount, vat in self.get_data():
            total += price * quantity * (1 - discount*.01) * (1.1 if vat else 1.0)
        self.total.set(currency_format(total))


# tab nhập hàng
class BuyingTab(BaseBillingTab):
    InfoForm = BuyingInfoForm
    partners_table = "providers"
    is_selling = False
    
    def partner_check(self, cursor, partner_info):
        provider_name, phone = partner_info
        
        if not provider_name:
            # Nếu bỏ trống
            msgBox = messagebox.askquestion("Thiếu thông tin",
                                            "Nhập mà không có thông tin nhà cung cấp?",
                                            icon="warning")
            if msgBox == 'yes':
                return 0,
            else:
                messagebox.showinfo("Thất bại", "Nhập hóa đơn thất bại")
                return
        else:
            # kiểm tra xem nhà cung cấp đã được lưu chưa
            ret = create_if_not_exists(cursor, table="providers", searchby="name",
                                       valuesdict={"name": provider_name, "phone": phone, "note": ""},
                                       prompt=("Nhà cung cấp", "Lưu hóa đơn"))
            if ret is not None:
                self.update_partners()
                return ret
            else:
                return
    
    def update_partners(self):
        provider_names = get_names_from_table("providers")
        self.info_form.providerE["values"] = provider_names
    
    def bind_partner_autofill_callback(self):
        def fill_provider(event):
            # kết nối với CSDL
            conn = db.connect(DATABASE)
            c = conn.cursor()
            c.execute("SELECT * FROM providers WHERE name = (?)", (self.info_form.provider.get(),))
            try:
                id, name, phone, note = c.fetchone()
                self.info_form.phone.set(phone)
            except TypeError as e:
                if "NoneType object" not in str(e):
                    raise e
            
            conn.close()
        self.info_form.providerE.bind("<<ComboboxSelected>>", fill_provider)


# tab bán hàng
class SellingTab(BaseBillingTab):
    InfoForm = SellingInfoForm
    partners_table = "customers"
    is_selling = True
    
    def partner_check(self, cursor, partner_info):
        customer_name, age, phone, email = partner_info
        birth_year = current_year() - age
        
        if not customer_name:
            # Nếu bỏ trống
            msgBox = messagebox.askquestion("Thiếu thông tin",
                                            "Nhập mà không có thông tin khách hàng?",
                                            icon="warning")
            if msgBox == 'yes':
                return 0,
            else:
                messagebox.showinfo("Thất bại", "Nhập hóa đơn thất bại")
                return
        else:
            # kiểm tra xem nhà cung cấp đã được lưu chưa
            ret = create_if_not_exists(cursor, table="customers", searchby="name",
                                       valuesdict={"name": customer_name, "birth_year": birth_year,
                                                   "phone": phone, "email": email, "note": ""},
                                       prompt=("Nhà cung cấp", "Lưu hóa đơn"))
            if ret is not None:
                customer_id, customer_name, birth_year, phone, email, customer_note = ret
                self.update_partners()
                age = current_year() - birth_year
                return customer_id, customer_name, age, phone, email, customer_note
            else:
                return
    
    def update_partners(self):
        customer_names = get_names_from_table("customers")
        self.info_form.customerE["values"] = customer_names
    """
    def update_products(self):
        customer_names = get_names_from_table("customers")
        self.info_form.customerE["values"] = customer_names
    """
    def bind_partner_autofill_callback(self):
        def fill_customer(event):
            # kết nối với CSDL
            conn = db.connect(DATABASE)
            c = conn.cursor()
            c.execute("SELECT * FROM customers WHERE name = (?)", (self.info_form.customer.get(),))
            try:
                id, name, birth_year, phone, email, note = c.fetchone()
                self.info_form.age.set(age)
                self.info_form.phone.set(phone)
                self.info_form.email.set(email)
            except TypeError as e:
                if "NoneType object" not in str(e):
                    raise e
            
            conn.close()
        self.info_form.customerE.bind("<<ComboboxSelected>>", fill_customer)
    """
    def bind_product_autofill_callback(self):
        # Định nghĩa callback cho mục điền sản phẩm
        def callback_fill_product(key, var):
            # kết nối với CSDL
            conn = db.connect(DATABASE)
            c = conn.cursor()
            c.execute(f"SELECT * FROM products WHERE {key} = (?)", (var.get(),))
            try:
                product_id, product_name, unit, price, note = c.fetchone()
                self.add_item_form.id.set(product_id)
                self.add_item_form.name.set(product_name)
                self.add_item_form.unit.set(unit)
                self.add_item_form.price.set(price)
            except TypeError as e:
                if "NoneType object" not in str(e):
                    raise e
            conn.close()
        self.add_item_form.id.trace_add("write", lambda var, index, mode: callback_fill_product("id", self.add_item_form.id))
        self.add_item_form.nameE.bind("<<ComboboxSelected>>",
                                      lambda event: callback_fill_product("name", self.add_item_form.name))
"""

# các chương trình con
def create_if_not_exists(cursor, table, searchby, valuesdict, prompt=None): # prompt = (tên dữ liệu, tên tác vụ)
    # xây dựng chuỗi truy vấn
    if isinstance(searchby, str):
        searchby = searchby,
    placeholder = ','.join(['?']*len(searchby))
    searchvalues = tuple(valuesdict[k] for k in searchby)
    searchby = ','.join(searchby)
    query = "SELECT * FROM {} WHERE ({}) = ({})".format(table, searchby, placeholder)
    
    cursor.execute(query, searchvalues)
    data = cursor.fetchall()
    if len(data) > 1:
        raise ValueError(f"duplicate {table}")
    elif len(data) == 1:
        return data[0]
    else:   # nếu chưa lưu thì lưu nhà cung cấp
        if prompt is not None:
            msgBox = messagebox.askquestion("Chưa có dữ liệu",
                                            f"{prompt[0]} chưa có trong danh sách, lưu mới?",
                                            icon="warning")
            if msgBox != 'yes':
                messagebox.showinfo("Thất bại", f"{prompt[1]} thất bại")
                return
        cursor.execute(f"INSERT INTO {table} ({','.join(valuesdict)}) VALUES ({','.join(['?']*len(valuesdict))})",
                       tuple(valuesdict.values()))
        cursor.execute(query, searchvalues)
        return cursor.fetchone()

def get_names_from_table(table):
    conn = db.connect(DATABASE)
    c = conn.cursor()
    
    c.execute(f'SELECT name FROM {table}')
    fetched = c.fetchall()
    
    conn.close()
    return [name for name, in fetched]
