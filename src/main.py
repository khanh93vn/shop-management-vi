#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

from billing import BuyingTab, SellingTab
from tableview import (
    ProductsViewTab, SuppliersViewTab, CustomersViewTab,
    BillsViewTab, BatchesViewTab, StockViewTab,
)
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
    
    # bán hàng/nhập hàng
    root_sell = SellingTab(tabs)
    root_buy = BuyingTab(tabs)
    tabs.add(root_sell, text="Bán hàng")
    tabs.add(root_buy, text="Nhập hàng")
    
    # quản lý dữ liệu
    data_management_tabs = ttk.Notebook(tabs)
    
    for TabCls, title in [(ProductsViewTab, "Sản phẩm"),
                          (SuppliersViewTab, "Nhà cung cấp"),
                          (CustomersViewTab, "Khách hàng"),
                          (BillsViewTab, "Hóa đơn"),
                          (BatchesViewTab, "Lô nhập/xuất"),
                          (StockViewTab, "Kho")]:
        tab = TabCls(data_management_tabs)
        data_management_tabs.add(tab, text=title)
    data_management_tabs.pack(expand = 1, fill ="both")
    tabs.add(data_management_tabs, text="Quản lý dữ liệu (sử dụng cẩn thận)")
    
    tabs.pack(expand = 1, fill ="both")
    window.mainloop()