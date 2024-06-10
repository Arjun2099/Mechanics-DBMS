import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import get_db_connection
import owner_dashboard
import psycopg2

class WorkshopDashboard:
    def __init__(self, root, owner_id, workshop_id):
        self.root = root
        self.owner_id = owner_id
        self.workshop_id = workshop_id
        self.root.title("Workshop Dashboard")
        self.root.geometry("1200x600")

        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        self.spare_tree = None  # Initialize spare_tree to None

        self.setup_dashboard()

    def setup_dashboard(self):
        self.clear_frame()
        workshop_name = self.get_workshop_name()
        tk.Label(self.main_frame, text=f"{workshop_name} Dashboard", font=("Helvetica", 16)).pack(pady=10)

        # Add a back button
        tk.Button(self.main_frame, text="Back", command=self.go_back).pack(side=tk.LEFT, anchor=tk.NW, padx=10, pady=10)
        
        tk.Button(self.main_frame, text="Manage Spare Parts", command=self.manage_spare_parts).pack(pady=5)
        
        tk.Button(self.main_frame, text="Add New Spare Parts", command=self.add_new_spare_parts).pack(pady=5)

    def get_workshop_name(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Workshop_Name FROM Workshop WHERE Workshop_Id = %s", (self.workshop_id,))
        workshop_name = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return workshop_name

    def manage_spare_parts(self):
        self.clear_frame()
        self.show_spare_parts()

    def show_spare_parts(self):
        tk.Label(self.main_frame, text="Manage Spare Parts", font=("Helvetica", 16)).pack(pady=10)

        # Add a back button
        back_button = tk.Button(self.main_frame, text="Back", command=self.setup_dashboard)
        back_button.pack(side=tk.LEFT, anchor=tk.NW, padx=10, pady=10)
        
        self.filter_var = tk.StringVar(self.main_frame)
        self.filter_var.set("All")
        self.filter_menu = tk.OptionMenu(self.main_frame, self.filter_var, "All", "In Stock", "Out of Stock", command=self.filter_spare_parts)
        self.filter_menu.pack(pady=5)

        self.spare_tree = ttk.Treeview(self.main_frame, columns=("Spare ID", "Spare Name", "Spare Number", "Available", "Price"), show='headings')
        self.spare_tree.heading("Spare ID", text="Spare ID")
        self.spare_tree.heading("Spare Name", text="Spare Name")
        self.spare_tree.heading("Spare Number", text="Spare Number")
        self.spare_tree.heading("Available", text="Available")
        self.spare_tree.heading("Price", text="Price")

        self.spare_tree.pack(expand=True, fill=tk.BOTH)
        self.load_spare_parts()

    def load_spare_parts(self):
        if self.spare_tree:
            self.spare_tree.delete(*self.spare_tree.get_children())
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Spare_Part_Id, Spare_Name, Spare_Part_No, Spare_Quantity_Available, Spare_Price 
                FROM Spare
                WHERE Workshop_Id = %s
            """, (self.workshop_id,))
            spare_parts = cursor.fetchall()
            cursor.close()
            conn.close()

            for part in spare_parts:
                self.spare_tree.insert('', 'end', values=part)

    def filter_spare_parts(self, filter_option):
        self.spare_tree.delete(*self.spare_tree.get_children())
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT Spare_Part_Id, Spare_Name, Spare_Part_No, Spare_Quantity_Available, Spare_Price 
            FROM Spare
            WHERE Workshop_Id = %s
        """ 
        if filter_option == "In Stock":
            query += " AND Spare_Quantity_Available > 0"
        elif filter_option == "Out of Stock":
            query += " AND Spare_Quantity_Available = 0"

        cursor.execute(query, (self.workshop_id,))
        spare_parts = cursor.fetchall()
        cursor.close()
        conn.close()

        for part in spare_parts:
            self.spare_tree.insert('', 'end', values=part)

    def add_new_spare_parts(self):
        self.new_spare_parts_window = tk.Toplevel(self.root)
        self.new_spare_parts_window.title("Add New Spare Parts")

        self.new_spare_parts_frame = tk.Frame(self.new_spare_parts_window, padx=10, pady=10)
        self.new_spare_parts_frame.pack(expand=True, fill=tk.BOTH)

        # Generate a unique spare part ID
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(Spare_Part_Id) FROM Spare")
        max_id = cursor.fetchone()[0]
        if max_id is None:
            max_id = 0
        spare_id = max_id + 1
        cursor.close()
        conn.close()

        tk.Label(self.new_spare_parts_frame, text="Spare Part ID").grid(row=0, column=0, pady=5)
        tk.Entry(self.new_spare_parts_frame, state="readonly", textvariable=tk.StringVar(value=spare_id)).grid(row=0, column=1, pady=5)

        tk.Label(self.new_spare_parts_frame, text="Spare Name").grid(row=1, column=0, pady=5)
        self.spare_name_entry = tk.Entry(self.new_spare_parts_frame)
        self.spare_name_entry.grid(row=1, column=1, pady=5)

        tk.Label(self.new_spare_parts_frame, text="Spare Number").grid(row=2, column=0, pady=5)
        self.spare_number_entry = tk.Entry(self.new_spare_parts_frame)
        self.spare_number_entry.grid(row=2, column=1, pady=5)

        tk.Label(self.new_spare_parts_frame, text="Quantity Available").grid(row=3, column=0, pady=5)
        self.quantity_entry = tk.Entry(self.new_spare_parts_frame)
        self.quantity_entry.grid(row=3, column=1, pady=5)

        tk.Label(self.new_spare_parts_frame, text="Price").grid(row=4, column=0, pady=5)
        self.price_entry = tk.Entry(self.new_spare_parts_frame)
        self.price_entry.grid(row=4, column=1, pady=5)

        # Button to add the spare part to the table
        tk.Button(self.new_spare_parts_frame, text="Add", command=self.add_spare_part).grid(row=5, columnspan=2, pady=5)

        # Button to finish adding spare parts
        tk.Button(self.new_spare_parts_frame, text="Done", command=self.new_spare_parts_window.destroy).grid(row=6, columnspan=2, pady=5)

    def add_spare_part(self):
        # Get the details of the new spare part
        spare_name = self.spare_name_entry.get()
        spare_number = self.spare_number_entry.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()

        # Validate input
        if not spare_name or not spare_number or not quantity or not price:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        # Check if a spare part with the same name and number already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Spare WHERE Spare_Name = %s AND Spare_Part_No = %s", (spare_name, spare_number))
        existing_spare = cursor.fetchone()
        cursor.close()
        conn.close()

        if existing_spare:
            messagebox.showerror("Error", "Spare part with the same name and number already exists")
            return

        # Insert the spare part into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Spare (Spare_Name, Spare_Part_No, Spare_Quantity_Available, Spare_Price, Workshop_Id) 
                VALUES (%s, %s, %s, %s, %s)
            """, (spare_name, spare_number, quantity, price, self.workshop_id))
            conn.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add spare part: {e}")
            return
        finally:
            cursor.close()
            conn.close()

        # Show success message
        messagebox.showinfo("Success", "Spare part added successfully")

        # Destroy the existing "Add New Spare Parts" window
        self.new_spare_parts_window.destroy()

        # Open a new "Add New Spare Parts" window
        self.add_new_spare_parts()

        # Reload the spare parts table
        self.load_spare_parts()



    def go_back(self):
        self.root.destroy()
        root = tk.Tk()
        app = owner_dashboard.OwnerDashboard(root, self.owner_id)
        root.mainloop()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()

def main(owner_id, workshop_id):
    root = tk.Tk()
    app = WorkshopDashboard(root, owner_id, workshop_id)
    root.mainloop()

if __name__ == "__main__":
    main(owner_id=1, workshop_id=1)
