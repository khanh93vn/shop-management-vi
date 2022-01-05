#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

from billing import BuyingTab, SellingTab
from tableview import ProductViewTab
from utils import *

if __name__ == "__main__":
    # root window
    window = tk.Tk()
    window.title("Nhà thuốc Thanh Tùng")
    window.geometry(GEO_WINDOW)
    window.pack_propagate(False)
    window.resizable(0, 0)

    # tabs
    tabs = ttk.Notebook(window)
    root_sell = SellingTab(tabs)
    root_buy = BuyingTab(tabs)
    tabs.add(root_sell, text="Bán hàng")
    tabs.add(root_buy, text="Nhập hàng")
    root_products = ProductViewTab(tabs)
    tabs.add(root_products, text="Sản phẩm")
    tabs.pack(expand = 1, fill ="both")
    window.mainloop()