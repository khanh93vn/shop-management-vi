import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox
import sqlite3 as db

from form import Textbox, Date, Form
from utils import *


# item units
itemUnits = [
    "cái",
    "chai",
    "gói",
    "hộp",
    "vỉ",
    "viên",
]

# form thêm sản phẩm
fields = [
    # name, description, type, unit
    ("id", "Mã hàng", tk.StringVar, None),                      # Mã mặt hàng
    ("name", "Tên mặt hàng", tk.StringVar, None),               # Tên mặt hàng
    ("unit", "Đơn vị tính", (tk.StringVar, itemUnits), None),   # Đơn vị tính
    ("price", "Đơn giá", tk.IntVar, "đồng"),                    # Đơn giá
    ("quantity", "Số lượng", tk.IntVar, "$unit"),               # Số lượng
    ("discount", "Chiết khấu", tk.DoubleVar, "%"),              # Chiết khấu
    ("vat", "Tính thuế VAT", tk.BooleanVar, None),              # VAT
]

# màn hình chính của tab
class StockForm(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # frame điền thông tin đơn hàng ở góc trên bên trái
        self.generalInfoForm = GeneralInfoForm(self)
        self.generalInfoForm.place(relx=0.01, rely=0.01, relwidth=0.5, relheight=0.29)
        
        # frame thêm sản phẩm ở góc dưới bên trái
        self.addItemForm = AddItemForm(self)
        self.addItemForm.place(relx=0.01, rely=0.31, relwidth=0.5, relheight=0.69)
        
        # ô xem các sản phẩm đã thêm ở bên phải
        self.itemView = ItemView(self)
        self.itemView.place(relx=0.52, rely=0.01, relwidth=0.5, relheight=0.88)
        
        # nút nhập hàng
        self.addItemButton = tk.Button(self, command=self.stockImport, text="Nhập hàng", font=DEFAULT_FONT)
        self.addItemButton.place(relx=0.52, rely=0.89, relheight=0.09, relwidth=0.5)
    
    def addItem(self):
        self.itemView.addItem(self.addItemForm.getData())
    
    def replaceItem(self):
        self.itemView.replaceItem(self.addItemForm.getData())
    
    def stockImport(self):
        # kết nối với CSDL
        conn = db.connect("data.db")
        c = conn.cursor()
        
        date, provider, note = self.generalInfoForm.getData()
        # kiểm tra xem nhà cung cấp đã được lưu chưa
        c.execute("SELECT * FROM providers WHERE name = (?)", provider)
        
        #
        MsgBox = tk.messagebox.askquestion ('Exit Application','Are you sure you want to exit the application',icon = 'warning')
        if MsgBox == 'yes':
            root.destroy()
        else:
            tk.messagebox.showinfo('Return','You will now return to the application screen')
        
        # ngắt kết nối với CSDL
        conn.commit()
        conn.close()

# frame thông tin chung
class GeneralInfoForm(Form):
    frameName = "Thông tin đơn hàng"
    fields = [
        # name, description, type, unit
        ("date", "Ngày hóa đơn", Date, None),
        ("provider", "Nhà cung cấp", tk.StringVar, None),
        ("note", "Ghi chú", Textbox, None),
    ]
"""
class GeneralInfoForm(ttk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, text="Thông tin đơn hàng",**kwargs)
        
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=3)
        
        # Ngày hóa đơn
        self.dateL = tk.Label(self, text="Ngày hóa đơn:", font=DEFAULT_FONT)
        self.dateL.grid(row=0, column=0, padx=relativeW(3), pady=relativeH(3), sticky='w')
        self.dateE = DateEntry(self, width=relativeW(25), font=DEFAULT_FONT)
        self.dateE.grid(row=0, column=1, padx=relativeW(3), pady=relativeH(3), sticky='we')
        
        # Nhà cung cấp
        var = tk.StringVar()
        w = tk.Label(self, text="Nhà cung cấp:", font=DEFAULT_FONT)
        w.grid(row=1, column=0, padx=relativeW(3), pady=relativeH(3), sticky='w')
        self.providerL = w
        w = tk.Entry(self, textvariable=var, width=relativeW(25), font=DEFAULT_FONT)
        w.grid(row=1, column=1, padx=relativeW(3), pady=relativeH(3), sticky='we')
        self.providerE = w
        self.provider = var
        
        # Ghi chú
        w = tk.Label(self, text="Ghi chú:", font=DEFAULT_FONT)
        w.grid(row=2, column=0, padx=relativeW(3), pady=relativeH(3), sticky='w')
        self.noteL = w
        w = tk.Text(self, width=relativeW(25), height=relativeH(5), font=DEFAULT_FONT)
        w.grid(row=3, column=0, columnspan=2,
               padx=relativeW(3), pady=relativeH(3), sticky='we')
        self.noteE = w
        
    def getData(self):
        return self.dateE.get_date(), self.provider.get(), self.noteE.get("1.0", "end-1c")
"""

# frame thêm sản phẩm
class AddItemForm(Form):
    frameName = "Thêm mặt hàng"
    fields = fields
"""
class AddItemForm(ttk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, text="Thêm mặt hàng",**kwargs)
        
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=10)
        self.columnconfigure(2, weight=3)
        # các ô dữ liệu
        for i, (name, desc, typ, unit) in enumerate(fields):
            # variable
            if isinstance(typ, tuple):
                typ, selection = typ
            var = typ()                                                                 # tạo biến
            setattr(self, name, var)                                                    # lưu biến
            
            # description
            w = tk.Label(self, text=desc + ':', anchor=tk.W, font=DEFAULT_FONT)         # tạo widget
            w.grid(row=i, column=0, padx=relativeW(3), pady=relativeH(3), sticky='w')   # đặt widget
            setattr(self, name + 'L', w)                                                # lưu widget
            
            # entry
            try:
                w = tk.OptionMenu(self, var, *selection)
                w["width"] = relativeW(2)
                w["font"] = DEFAULT_FONT
                w.grid(row=i, column=2, padx=relativeW(3), pady=relativeH(3), sticky='we')
                del selection
            except UnboundLocalError as e:
                if "local variable 'selection' referenced before assignment" not in str(e):
                    raise e
                if isinstance(var, (tk.StringVar, tk.IntVar, tk.DoubleVar)):
                    w = tk.Entry(self, textvariable=var, width=relativeW(25), font=DEFAULT_FONT)
                elif isinstance(var, tk.BooleanVar):
                    w = tk.Checkbutton(self, variable=var, width=relativeW(25), font=DEFAULT_FONT)
            w.grid(row=i, column=1, padx=relativeW(3), pady=relativeH(3), sticky='we')
            setattr(self, name + 'E', w)
            
            # unit
            if unit is not None:
                if unit[0] == "$":
                    text = getattr(self, unit[1:])
                else:
                    text = unit
                w = tk.Label(self, text=text, anchor=tk.E, font=DEFAULT_FONT)
                w.grid(row=i, column=2, padx=relativeW(3), pady=relativeH(3), sticky='e')
                setattr(self, name + 'U', w)
                if isinstance(text, tk.StringVar):
                    w.configure(textvariable=text)
    
    def getData(self):
        return tuple(getattr(self, name).get() for name, *_ in fields)
"""

class ItemView(ttk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, text="Hóa đơn",**kwargs)
        container = args[0]
        
        self.columnconfigure(0, weight=7)
        self.columnconfigure(1, weight=6)
        self.columnconfigure(2, weight=6)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=50)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=3)
        
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
        self.table["columns"] = tuple(range(len(fields)))
        w = relativeW(100)//len(fields)
        for i, (_, desc, *_) in enumerate(fields):
            self.table.column(i, width=w, anchor ='c') # 'se'
            self.table.heading(i, text=desc)
        
        
        # nút thêm mới
        self.addItemButton = tk.Button(self, command=container.addItem, text="Thêm mới", font=DEFAULT_FONT)
        self.addItemButton.grid(row=2, column=0, sticky="nwes")
        
        # nút thay thế
        self.replaceItemButton = tk.Button(self, command=container.replaceItem, text="Sửa", font=DEFAULT_FONT)
        self.replaceItemButton.grid(row=2, column=1, sticky="nwes")
        
        # nút xóa
        self.deleteItemButton = tk.Button(self, command=self.deleteItem, text="Xóa", font=DEFAULT_FONT)
        self.deleteItemButton.grid(row=2, column=2, sticky="nwes")
        
    
    def addItem(self, newItem):
        self.table.insert("", 'end', values=newItem)
    
    def replaceItem(self, newItem):
        item = self.table.selection()[0]
        self.table.delete(item)
        self.table.insert("", int(item[1:]) - 1, values=newItem)
        
    
    def deleteItem(self):
        selected = self.table.selection()
        for item in selected:
            self.table.delete(item)
