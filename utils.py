import ctypes
import tkinter as tk

from datetime import date, datetime
from time import mktime

# đường dẫn CSDL
DATABASE = "data.db"

# geometries
RESOLUTION = [ctypes.windll.user32.GetSystemMetrics(i) for i in (0, 1)]
def relativeW(wrat):
    return int(RESOLUTION[0]*.001*wrat)
def relativeH(hrat):
    return int(RESOLUTION[1]*.001*hrat)
def relative_font_size(size):
    return int(RESOLUTION[1]*.001*size)
def get_geometry(wrat, hrat):
    return f"{relativeW(wrat)}x{relativeH(hrat)}"
GEO_WINDOW = get_geometry(700, 700)

# fonts
DEFAULT_FONT = ("default", relative_font_size(12))

# datetime
dtformat = "%d/%m/%Y"
def today():
    return date.today().strftime(dtformat)

def date2ts(s):
    if s == '--':
        return 0
    return int((mktime(datetime.strptime(s, dtformat).timetuple()) + 25200) / 86400)

def ts2date(ts):
    if ts == 0:
        return '--'
    return datetime.utcfromtimestamp(ts*86400 + 18000).strftime(dtformat)

# datatype conversion from strings
def dataconv(typ):
    if typ == tk.IntVar:
        return int
    elif typ == tk.DoubleVar:
        return float
    elif typ == tk.BooleanVar:
        return lambda s: False if s == "False" else True
    else:
        return lambda s: s

# định dạng tiền tệ
def currency_format(amount):
    currency = "{:,.2f}".format(amount)
    main, fractional = currency.split('.')
    main = main.replace(',', '.')
    fractional = fractional.replace(',', '.')
    return f"{main},{fractional} đồng"


# units
item_units = [
    "cái",
    "chai",
    "gói",
    "hộp",
    "vỉ",
    "viên",
]