import tkinter as tk
from tkcalendar import DateEntry
from tkinter import ttk

from utils import *

class Textbox(tk.Text):
    def get(self, index1=1.0, index2=tk.END):
        return super().get(index1, index2)

    def set(self, txt):
        self.delete(1.0, tk.END)
        self.insert(1.0, txt)

class Date(DateEntry):
    def get(self):
        return date2ts(super().get())
    
    def set(self, timestamp):
        try:
            self.set_date(ts2date(int(timestamp)))
        except TypeError as e:
            print(ts2date(int(timestamp)))
            raise SystemError("idk")
            

class Form(ttk.LabelFrame):
    def __init__(self, *args, weights=(5, 10, 3), **kwargs):
        super().__init__(*args, text=self.frame_name,**kwargs)
        
        self.columnconfigure(0, weight=weights[0])
        self.columnconfigure(1, weight=weights[1])
        self.columnconfigure(2, weight=weights[2])
        # các ô dữ liệu
        row = 0
        for name, desc, typ, unit in self.fields:
            # variable
            if isinstance(typ, tuple):
                typ, selection = typ
            if typ == Textbox:
                var = typ(self, width=relativeW(25), height=relativeH(5), font=DEFAULT_FONT)
            elif typ == Date:
                var = typ(self, width=relativeW(25), date_pattern='dd/mm/yyyy', font=DEFAULT_FONT)
            else:
                var = typ()                                                             # tạo biến
            setattr(self, name, var)                                                    # lưu biến
            
            # description
            w = tk.Label(self, text=desc + ':', anchor=tk.W, font=DEFAULT_FONT)         # tạo widget
            w.grid(row=row, column=0, padx=relativeW(3), pady=relativeH(3), sticky='w') # đặt widget
            setattr(self, name + 'L', w)                                                # lưu widget
            
            # entry
            colspan = 1
            col = 1
            try:
                w = ttk.Combobox(self, textvariable=var, values=selection,
                                 width=relativeW(2), font=DEFAULT_FONT)
                w.grid(row=row, column=2, padx=relativeW(3), pady=relativeH(3), sticky='we')
                del selection
            except UnboundLocalError as e:
                if "local variable 'selection' referenced before assignment" not in str(e):
                    raise e
                if isinstance(var, (tk.StringVar, tk.IntVar, tk.DoubleVar)):
                    w = tk.Entry(self, textvariable=var, width=relativeW(25), font=DEFAULT_FONT)
                elif isinstance(var, tk.BooleanVar):
                    w = tk.Checkbutton(self, variable=var, width=relativeW(25), font=DEFAULT_FONT)
                elif isinstance(var, Textbox):
                    w = var
                    row += 1
                    col = 0
                    colspan = 2
                elif isinstance(var, Date):
                    w = var
            w.grid(row=row, column=col, columnspan=colspan, padx=relativeW(3), pady=relativeH(3), sticky='we')
            setattr(self, name + 'E', w)
            
            # unit
            if unit is not None:
                if unit[0] == "$":
                    text = getattr(self, unit[1:])
                else:
                    text = unit
                w = tk.Label(self, text=text, anchor=tk.E, font=DEFAULT_FONT)
                w.grid(row=row, column=2, padx=relativeW(3), pady=relativeH(3), sticky='e')
                setattr(self, name + 'U', w)
                if isinstance(text, tk.StringVar):
                    w.configure(textvariable=text)
            row += 1
    
    def get_data(self):
        return tuple(getattr(self, name).get() for name, *_ in self.fields)
    
    def set_data(self, data):
        for datum, (name, *_) in zip(data, self.fields):
            getattr(self, name).set(datum)
