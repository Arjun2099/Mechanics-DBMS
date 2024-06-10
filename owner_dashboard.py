import tkinter as tk
from tkinter import messagebox, ttk
from db_connection import get_db_connection
import workshop_dashboard
import login

class OwnerDashboard:
    def __init__(self, root, owner_id):
        self.root = root
        self.owner_id = owner_id
        self.root.title("Owner Dashboard")
        self.root.geometry("600x400")

        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.create_workshop_frame = tk.Frame(self.main_frame)
        self.manage_workshop_frame = tk.Frame(self.main_frame)

        self.setup_dashboard()
        
        self.home_button = tk.Button(self.main_frame, text="Home", command=self.go_to_home)
        self.home_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    def go_to_home(self):
        # Destroy current dashboard and go to login page
        self.root.destroy()
        root = tk.Tk()
        app = login.LoginApp(root)
        root.mainloop()

    def setup_dashboard(self):
        tk.Label(self.main_frame, text="Owner Dashboard", font=("Helvetica", 16)).pack(pady=10)

        tk.Button(self.main_frame, text="Create Workshop", command=self.create_workshop).pack(pady=5)
        tk.Button(self.main_frame, text="Manage Workshops", command=self.manage_workshops).pack(pady=5)

        self.show_workshops()

    def create_workshop(self):
        self.clear_frame()

        tk.Label(self.create_workshop_frame, text="Workshop Name").grid(row=0, column=0, pady=5)
        self.workshop_name_entry = tk.Entry(self.create_workshop_frame)
        self.workshop_name_entry.grid(row=0, column=1, pady=5)

        tk.Button(self.create_workshop_frame, text="Create", command=self.save_workshop).grid(row=1, column=0, columnspan=2, pady=5)

        self.create_workshop_frame.pack(expand=True)

    def save_workshop(self):
        workshop_name = self.workshop_name_entry.get()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Workshop (Workshop_Name) VALUES (%s) RETURNING Workshop_Id", (workshop_name,))
        workshop_id = cursor.fetchone()[0]
        conn.commit()
        cursor.execute("INSERT INTO Ownership (Workshop_Id, User_Id) VALUES (%s, %s)", (workshop_id, self.owner_id))
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", "Workshop created successfully!")
        self.create_workshop_frame.pack_forget()
        self.setup_dashboard()

    def manage_workshops(self):
        self.clear_frame()
        self.show_workshops()

    def show_workshops(self):
        self.clear_frame()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT w.Workshop_Id, w.Workshop_Name 
            FROM Workshop w
            INNER JOIN Ownership o ON w.Workshop_Id = o.Workshop_Id
            WHERE o.User_Id = %s
        """, (self.owner_id,))
        workshops = cursor.fetchall()
        cursor.close()
        conn.close()

        if not workshops:
            tk.Label(self.main_frame, text="You have no workshops. Create your first workshop!", font=("Helvetica", 14)).pack(pady=10)
            tk.Button(self.main_frame, text="Create Workshop", command=self.create_workshop).pack(pady=10)
        else:
            self.workshop_tree = ttk.Treeview(self.main_frame, columns=("Workshop ID", "Workshop Name"), show='headings')
            self.workshop_tree.heading("Workshop ID", text="Workshop ID")
            self.workshop_tree.heading("Workshop Name", text="Workshop Name")

            for workshop in workshops:
                self.workshop_tree.insert('', 'end', values=workshop)

            self.workshop_tree.pack(expand=True, fill=tk.BOTH)
            self.workshop_tree.bind('<<TreeviewSelect>>', self.on_workshop_select)

            self.confirm_button = tk.Button(self.main_frame, text="Confirm", command=self.confirm_selection)
            self.confirm_button.pack(pady=5)
            self.confirm_button.config(state=tk.DISABLED)

            tk.Button(self.main_frame, text="Create New Workshop", command=self.create_workshop).pack(pady=5)

    def on_workshop_select(self, event):
        selected_item = self.workshop_tree.selection()
        if selected_item:
            self.confirm_button.config(state=tk.NORMAL)
        else:
            self.confirm_button.config(state=tk.DISABLED)

    def confirm_selection(self):
        selected_item = self.workshop_tree.selection()[0]
        workshop_id = self.workshop_tree.item(selected_item)['values'][0]
        self.open_workshop_dashboard(workshop_id)

    def open_workshop_dashboard(self, workshop_id):
        self.root.destroy()
        workshop_dashboard.main(self.owner_id, workshop_id)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    owner_id = 1  # This should be passed based on the logged-in owner
    app = OwnerDashboard(root, owner_id)
    root.mainloop()
