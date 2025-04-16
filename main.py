from fpdf import FPDF
import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import os
import hashlib
import random

# 1. Add Customers First
# 2. Create Quotation
# 3. Create Invoice
# 4. Create Receipt

class InvoiceSystem:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Invoice System")
        self.window.geometry("400x300")
        self.setup_folders()
        self.setup_database()
        self.create_main_menu()

    def setup_folders(self):
        # Create necessary folders if they don't exist
        folders = ['database', 'templates', 'output']
        for folder in folders:
            folder_path = os.path.join(os.path.dirname(__file__), folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

    def setup_database(self):
        db_path = os.path.join(os.path.dirname(__file__), 'database', 'invoice_system.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Create necessary tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                address TEXT,
                phone TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                date TEXT,
                total REAL,
                type TEXT
            )
        ''')
        self.conn.commit()

    def create_main_menu(self):
        tk.Button(self.window, text="Create Quotation", command=self.create_quotation).pack(pady=10)
        tk.Button(self.window, text="Create Invoice", command=self.create_invoice).pack(pady=10)
        tk.Button(self.window, text="Create Receipt", command=self.create_receipt).pack(pady=10)
        tk.Button(self.window, text="Customer Management", command=self.manage_customers).pack(pady=10)
        tk.Button(self.window, text="Exit", command=self.window.quit).pack(pady=10)

    def create_quotation(self):
        self.generate_document("Quotation")

    def create_invoice(self):
        self.generate_document("Invoice")

    def create_receipt(self):
        self.generate_document("Receipt")

    def generate_document(self, doc_type):
        # Create document form window
        doc_window = tk.Toplevel(self.window)
        doc_window.title(f"Create {doc_type}")
        doc_window.geometry("400x300")

        # Customer selection
        tk.Label(doc_window, text="Select Customer:").pack(pady=5)
        customer_var = tk.StringVar()
        customer_menu = tk.OptionMenu(doc_window, customer_var, "")
        customer_menu.pack()

        # Amount entry
        tk.Label(doc_window, text="Amount:").pack(pady=5)
        amount_entry = tk.Entry(doc_window)
        amount_entry.pack()

        # Populate customer dropdown
        self.cursor.execute('SELECT name FROM customers')
        customers = self.cursor.fetchall()
        menu = customer_menu["menu"]
        menu.delete(0, "end")
        for customer in customers:
            menu.add_command(label=customer[0], 
            command=lambda name=customer[0]: customer_var.set(name))

        def create_pdf():
            if not customer_var.get() or not amount_entry.get():
                messagebox.showerror("Error", "Please select customer and enter amount")
                return

            # Create a dummy item list for testing
            items = [("Service Fee", 1, float(amount_entry.get()))]

            # Fetch customer details
            self.cursor.execute('SELECT address, phone FROM customers WHERE name = ?', (customer_var.get(),))
            customer = self.cursor.fetchone()

            if customer:
                customer_address = customer[0]
                # Random document number
                invoice_number = random.randint(100000, 999999)
            else:
                messagebox.showerror("Error", "Customer not found")
                return

            from document_templates import DocumentTemplate
            template = DocumentTemplate()
            pdf = template.generate(
                customer_name=customer_var.get(),
                customer_address=customer_address,
                invoice_number=invoice_number,
                items=items
            )
            # Save
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
            filename = f"{doc_type.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(output_dir, filename)
            pdf.output(filepath)
            messagebox.showinfo("Success", f"{doc_type} has been generated as {filename}")
            doc_window.destroy()


        tk.Button(doc_window, text=f"Generate {doc_type}", command=create_pdf).pack(pady=20)

    def manage_customers(self):
        # Create customer management window
        customer_window = tk.Toplevel(self.window)
        customer_window.title("Customer Management")
        customer_window.geometry("300x200")
        
        tk.Button(customer_window, text="Add Customer", command=self.add_customer).pack(pady=10)
        tk.Button(customer_window, text="View Customers", command=self.view_customers).pack(pady=10)

    def add_customer(self):
        # Create customer form window
        form_window = tk.Toplevel(self.window)
        form_window.title("Add New Customer")
        form_window.geometry("300x250")

        # Create form fields
        tk.Label(form_window, text="Name:").pack(pady=5)
        name_entry = tk.Entry(form_window)
        name_entry.pack()

        tk.Label(form_window, text="Address:").pack(pady=5)
        address_entry = tk.Entry(form_window)
        address_entry.pack()

        tk.Label(form_window, text="Phone:").pack(pady=5)
        phone_entry = tk.Entry(form_window)
        phone_entry.pack()

        def save_customer():
            name = name_entry.get()
            address = address_entry.get()
            phone = phone_entry.get()
            
            if name and address and phone:
                self.cursor.execute('''
                    INSERT INTO customers (name, address, phone)
                    VALUES (?, ?, ?)
                ''', (name, address, phone))
                self.conn.commit()
                messagebox.showinfo("Success", "Customer added successfully!")
                form_window.destroy()
            else:
                messagebox.showerror("Error", "All fields are required!")

        tk.Button(form_window, text="Save Customer", command=save_customer).pack(pady=20)

    def view_customers(self):
        view_window = tk.Toplevel(self.window)
        view_window.title("Customer List")
        view_window.geometry("400x300")

        # Create listbox
        listbox = tk.Listbox(view_window, width=50)
        listbox.pack(pady=10, padx=10)

        # Fetch and display customers
        self.cursor.execute('SELECT name, address, phone FROM customers')
        customers = self.cursor.fetchall()
        
        for customer in customers:
            listbox.insert(tk.END, f"Name: {customer[0]} - Phone: {customer[2]}")

class LoginSystem:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Login System")
        self.window.geometry("300x200")
        self.setup_database()
        self.create_login_form()

    def setup_database(self):
        db_path = os.path.join(os.path.dirname(__file__), 'database', 'invoice_system.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Create users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                email TEXT
            )
        ''')
        self.conn.commit()

    def create_login_form(self):
        tk.Label(self.window, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.window)
        self.username_entry.pack()

        tk.Label(self.window, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.window, show="*")
        self.password_entry.pack()

        tk.Button(self.window, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.window, text="Register", command=self.show_register).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username and password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                              (username, hashed_password))
            user = self.cursor.fetchone()
            
            if user:
                self.window.destroy()
                app = InvoiceSystem()
                app.window.mainloop()
            else:
                messagebox.showerror("Error", "Invalid username or password")
        else:
            messagebox.showerror("Error", "Please fill all fields")

    def show_register(self):
        register_window = tk.Toplevel(self.window)
        register_window.title("Register")
        register_window.geometry("300x250")

        tk.Label(register_window, text="Username:").pack(pady=5)
        username_entry = tk.Entry(register_window)
        username_entry.pack()

        tk.Label(register_window, text="Password:").pack(pady=5)
        password_entry = tk.Entry(register_window, show="*")
        password_entry.pack()

        tk.Label(register_window, text="Email:").pack(pady=5)
        email_entry = tk.Entry(register_window)
        email_entry.pack()

        def register():
            username = username_entry.get()
            password = password_entry.get()
            email = email_entry.get()

            if username and password and email:
                try:
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    self.cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                                      (username, hashed_password, email))
                    self.conn.commit()
                    messagebox.showinfo("Success", "Registration successful!")
                    register_window.destroy()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Username already exists")
            else:
                messagebox.showerror("Error", "Please fill all fields")

        tk.Button(register_window, text="Register", command=register).pack(pady=20)

    def run(self):
        self.window.mainloop()

# Modify the main execution
if __name__ == "__main__":
    login = LoginSystem()
    login.run()
