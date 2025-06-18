# inventory_management_system.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import datetime
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 username TEXT PRIMARY KEY, password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 quantity INTEGER NOT NULL,
                 price REAL NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 product_id INTEGER, quantity_sold INTEGER, date TEXT,
                 FOREIGN KEY(product_id) REFERENCES products(id))''')
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
    conn.commit()
    conn.close()

# ---------- DATABASE OPERATIONS ----------
def validate_user(username, password):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def add_product(name, quantity, price):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return products

def update_product(product_id, name, quantity, price):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("UPDATE products SET name=?, quantity=?, price=? WHERE id=?", (name, quantity, price, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

def get_low_stock(threshold=10):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE quantity < ?", (threshold,))
    items = c.fetchall()
    conn.close()
    return items

def record_sale(product_id, quantity):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    date = datetime.date.today().isoformat()
    c.execute("INSERT INTO sales (product_id, quantity_sold, date) VALUES (?, ?, ?)", (product_id, quantity, date))
    c.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (quantity, product_id))
    conn.commit()
    conn.close()

def get_sales_summary():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''SELECT p.name, SUM(s.quantity_sold) as total_sold, SUM(s.quantity_sold * p.price) as total_revenue
                 FROM sales s JOIN products p ON s.product_id = p.id
                 GROUP BY s.product_id''')
    data = c.fetchall()
    conn.close()
    return data

# ---------- UTILITIES ----------
def is_valid_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

FONT_LARGE = ("Arial", 14)

# ---------- MAIN CLASS ----------
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory System - Login")
        self.build_auth_ui()

    def build_auth_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Username", font=FONT_LARGE).grid(row=0, column=0, padx=10, pady=10)
        self.entry_user = tk.Entry(self.root, font=FONT_LARGE)
        self.entry_user.grid(row=0, column=1)

        tk.Label(self.root, text="Password", font=FONT_LARGE).grid(row=1, column=0, padx=10)
        self.entry_pass = tk.Entry(self.root, show="*", font=FONT_LARGE)
        self.entry_pass.grid(row=1, column=1)

        tk.Button(self.root, text="Login", command=self.login, font=FONT_LARGE).grid(row=2, column=0, pady=10)
        tk.Button(self.root, text="Register", command=self.register, font=FONT_LARGE).grid(row=2, column=1)

    def login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both fields")
            return
        if validate_user(username, password):
            self.build_dashboard_ui()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    def register(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both fields")
            return
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully. Please login.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        conn.close()

    def build_dashboard_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        selected_id = tk.StringVar()

        def refresh_table():
            for row in tree.get_children():
                tree.delete(row)
            for prod in get_all_products():
                tree.insert("", "end", values=prod)

        def select_item(event):
            item = tree.selection()
            if item:
                values = tree.item(item, "values")
                selected_id.set(values[0])
                entry_name.delete(0, tk.END)
                entry_name.insert(0, values[1])
                entry_qty.delete(0, tk.END)
                entry_qty.insert(0, values[2])
                entry_price.delete(0, tk.END)
                entry_price.insert(0, values[3])

        def add_item():
            name = entry_name.get()
            qty = entry_qty.get()
            price = entry_price.get()
            if name and qty.isdigit() and is_valid_number(price):
                add_product(name, int(qty), float(price))
                refresh_table()
            else:
                messagebox.showerror("Invalid Input", "Check name, quantity, and price")

        def update_item():
            if selected_id.get():
                update_product(int(selected_id.get()), entry_name.get(), int(entry_qty.get()), float(entry_price.get()))
                refresh_table()

        def delete_item():
            if selected_id.get():
                delete_product(int(selected_id.get()))
                refresh_table()

        def sell_item():
            if selected_id.get():
                qty = simpledialog.askinteger("Sell Product", "Enter quantity to sell:")
                if qty:
                    record_sale(int(selected_id.get()), qty)
                    refresh_table()

        def show_sales_report():
            data = get_sales_summary()
            if data:
                names = [d[0] for d in data]
                sold = [d[1] for d in data]
                plt.figure(figsize=(8, 4))
                plt.bar(names, sold, color='skyblue')
                plt.title("Sales Report")
                plt.xlabel("Product")
                plt.ylabel("Units Sold")
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()
            else:
                messagebox.showinfo("Info", "No sales data.")

        def show_low_stock():
            data = get_low_stock()
            if data:
                names = [d[1] for d in data]
                qtys = [d[2] for d in data]
                plt.figure(figsize=(6, 6))
                plt.pie(qtys, labels=names, autopct='%1.1f%%', startangle=90)
                plt.title("Low Stock Items")
                plt.axis('equal')
                plt.show()
            else:
                messagebox.showinfo("Low Stock", "All stock levels are sufficient.")

        # Input fields and buttons
        tk.Label(self.root, text="Name", font=FONT_LARGE).grid(row=0, column=0)
        entry_name = tk.Entry(self.root, font=FONT_LARGE)
        entry_name.grid(row=0, column=1)

        tk.Label(self.root, text="Quantity", font=FONT_LARGE).grid(row=0, column=2)
        entry_qty = tk.Entry(self.root, font=FONT_LARGE)
        entry_qty.grid(row=0, column=3)

        tk.Label(self.root, text="Price", font=FONT_LARGE).grid(row=0, column=4)
        entry_price = tk.Entry(self.root, font=FONT_LARGE)
        entry_price.grid(row=0, column=5)

        tk.Button(self.root, text="Add", command=add_item, font=FONT_LARGE).grid(row=0, column=6)
        tk.Button(self.root, text="Update", command=update_item, font=FONT_LARGE).grid(row=0, column=7)
        tk.Button(self.root, text="Delete", command=delete_item, font=FONT_LARGE).grid(row=0, column=8)
        tk.Button(self.root, text="Sell", command=sell_item, font=FONT_LARGE).grid(row=0, column=9)
        tk.Button(self.root, text="Sales Report", command=show_sales_report, font=FONT_LARGE).grid(row=0, column=10)
        tk.Button(self.root, text="Low Stock", command=show_low_stock, font=FONT_LARGE).grid(row=0, column=11)

        # Product Table
        tree = ttk.Treeview(self.root, columns=("ID", "Name", "Qty", "Price"), show="headings", height=15)
        for col in ("ID", "Name", "Qty", "Price"):
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')
        tree.grid(row=1, column=0, columnspan=12, padx=10, pady=10)
        tree.bind("<ButtonRelease-1>", select_item)

        refresh_table()

# ---------- MAIN ----------
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
