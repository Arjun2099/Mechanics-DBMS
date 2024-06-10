import bcrypt
import tkinter as tk
from tkinter import messagebox
from db_connection import get_db_connection
import datetime
from owner_dashboard import OwnerDashboard

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Workshop Management System")
        self.root.geometry("500x400")  # Set the window size

        self.login_frame = tk.Frame(root, padx=10, pady=10)
        self.register_frame = tk.Frame(root, padx=10, pady=10)

        self.setup_login()

    def setup_login(self):
        self.register_frame.pack_forget()
        self.login_frame.pack(expand=True)

        tk.Label(self.login_frame, text="Username").grid(row=0, column=0, pady=5)
        self.username = tk.Entry(self.login_frame)
        self.username.grid(row=0, column=1, pady=5)

        tk.Label(self.login_frame, text="Password").grid(row=1, column=0, pady=5)
        self.password = tk.Entry(self.login_frame, show='*')
        self.password.grid(row=1, column=1, pady=5)

        self.role = tk.StringVar(self.login_frame)
        self.role.set("Customer")
        self.role_menu = tk.OptionMenu(self.login_frame, self.role, "Customer", "Employee", "Owner", command=self.change_role_color)
        self.role_menu.config(width=15)  # Set fixed width for the option menu
        self.role_menu.grid(row=2, column=0, columnspan=2, pady=5)  # Center the option menu

        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(self.login_frame, text="Sign Up", command=self.setup_register).grid(row=4, column=0, columnspan=2, pady=5)

        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.grid_columnconfigure(1, weight=1)

        self.change_role_color("Customer")  # Initialize the color

    def change_role_color(self, role):
        role_colors = {
            "Customer": "lightblue",
            "Employee": "lightgreen",
            "Owner": "lightcoral"
        }
        self.role_menu.config(bg=role_colors.get(role, "white"))

    def login(self):
        username = self.username.get()
        password = self.password.get()
        role = self.role.get()

        # Validate user from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT User_Id, User_Name, Password FROM Users WHERE User_Name=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            user_id = user[0]
            user_name = user[1]
            messagebox.showinfo("Login Successful", f"Welcome {user_name}!")
            # Based on role, redirect to appropriate dashboard (Customer, Employee, Owner)
            if role == "Owner":
                self.login_frame.pack_forget()
                OwnerDashboard(self.root, user_id)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")

    def setup_register(self):
        self.login_frame.pack_forget()
        self.register_frame.pack(expand=True)

        tk.Label(self.register_frame, text="Username").grid(row=0, column=0, pady=5)
        self.reg_username = tk.Entry(self.register_frame)
        self.reg_username.grid(row=0, column=1, pady=5)

        tk.Label(self.register_frame, text="Password").grid(row=1, column=0, pady=5)
        self.reg_password = tk.Entry(self.register_frame, show='*')
        self.reg_password.grid(row=1, column=1, pady=5)

        tk.Label(self.register_frame, text="Email").grid(row=2, column=0, pady=5)
        self.reg_email = tk.Entry(self.register_frame)
        self.reg_email.grid(row=2, column=1, pady=5)

        tk.Label(self.register_frame, text="Phone No").grid(row=3, column=0, pady=5)
        self.reg_phone = tk.Entry(self.register_frame)
        self.reg_phone.grid(row=3, column=1, pady=5)

        tk.Label(self.register_frame, text="Address").grid(row=4, column=0, pady=5)
        self.reg_address = tk.Entry(self.register_frame)
        self.reg_address.grid(row=4, column=1, pady=5)

        tk.Label(self.register_frame, text="Role").grid(row=5, column=0, pady=5)
        self.reg_role = tk.StringVar(self.register_frame)
        self.reg_role.set("Customer")
        self.reg_role_menu = tk.OptionMenu(self.register_frame, self.reg_role, "Customer", "Employee", "Owner", command=self.display_additional_fields)
        self.reg_role_menu.grid(row=5, column=1, pady=5)

        self.additional_frame = tk.Frame(self.register_frame)
        self.additional_frame.grid(row=6, column=0, columnspan=2)

        self.display_additional_fields("Customer")

        button_frame = tk.Frame(self.register_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(button_frame, text="Sign Up", command=self.register, font=('Arial', 10), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Login", command=self.setup_login, font=('Arial', 10), width=10).pack(side=tk.RIGHT, padx=5)
        
        self.register_frame.grid_columnconfigure(0, weight=1)
        self.register_frame.grid_columnconfigure(1, weight=1)

    def display_additional_fields(self, role):
        for widget in self.additional_frame.winfo_children():
            widget.destroy()

        if role == "Employee":
            tk.Label(self.additional_frame, text="Salary").grid(row=0, column=0, pady=5)
            self.reg_salary = tk.Entry(self.additional_frame)
            self.reg_salary.grid(row=0, column=1, pady=5)

            tk.Label(self.additional_frame, text="Workshop ID").grid(row=2, column=0, pady=5)
            self.reg_workshop_id = tk.Entry(self.additional_frame)
            self.reg_workshop_id.grid(row=2, column=1, pady=5)
        elif role == "Owner":
            tk.Label(self.additional_frame, text="Total Capita").grid(row=0, column=0, pady=5)
            self.reg_total_capita = tk.Entry(self.additional_frame)
            self.reg_total_capita.grid(row=0, column=1, pady=5)

    def register(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        email = self.reg_email.get()
        phone = self.reg_phone.get()
        address = self.reg_address.get()
        role = self.reg_role.get()

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Get the current system date
        joining_date = datetime.datetime.now().strftime('%Y-%m-%d')

        # Insert the new user into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Users (User_Name, Phone_No, Email, Address, Password) VALUES (%s, %s, %s, %s, %s) RETURNING User_Id",
            (username, phone, email, address, hashed_password.decode('utf-8'))
        )
        user_id = cursor.fetchone()[0]

        # Insert additional role-based information
        if role == "Customer":
            total_visits = 0
            cursor.execute(
                "INSERT INTO Customer (User_Id, Total_Visits) VALUES (%s, %s)",
                (user_id, total_visits)
            )
        elif role == "Employee":
            salary = self.reg_salary.get()
            workshop_id = self.reg_workshop_id.get()
            cursor.execute(
                "INSERT INTO Employee (User_Id, Salary, Joining_Date, Workshop_Id) VALUES (%s, %s, %s, %s)",
                (user_id, salary, joining_date, workshop_id)
            )
        elif role == "Owner":
            total_capita = self.reg_total_capita.get()
            cursor.execute(
                "INSERT INTO Owner (User_Id, Total_Capita) VALUES (%s, %s)",
                (user_id, total_capita)
            )

        conn.commit()
        cursor.close()
        conn.close()

        messagebox.showinfo("Registration Successful", "You have successfully registered!")
        self.register_frame.pack_forget()
        self.setup_login()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
