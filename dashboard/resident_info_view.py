# dashboard/resident_info_view.py
import tkinter as tk
from tkinter import Frame, Label, Entry, Button, messagebox, Toplevel, StringVar, OptionMenu
import mysql.connector

data_frame = None
resident_rows = []
selected_index = None

def fetch_residents(status_filter=None):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="brgy_profiling_system"
        )
        cursor = conn.cursor()

        # Main query with subquery to count members per household
        query = """
            SELECT 
                r.id, 
                r.family_name, 
                r.address, 
                r.status, 
                (
                    SELECT COUNT(*) 
                    FROM individuals i 
                    WHERE i.resident_id = r.id
                ) AS members
            FROM residents r
        """

        if status_filter and status_filter != "All":
            query += " WHERE r.status = %s"
            cursor.execute(query, (status_filter,))
        else:
            cursor.execute(query)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching data: {err}")
        return []


def refresh_data(status_filter=None, custom_rows=None):
    for widget in data_frame.winfo_children():
        widget.destroy()

    global resident_rows
    resident_rows = custom_rows if custom_rows is not None else fetch_residents(status_filter)

    def on_row_click(event, index):
        for child in data_frame.winfo_children():
            child.config(bg="white")
        row_widgets = data_frame.grid_slaves(row=index)
        for widget in row_widgets:
            widget.config(bg="#d1e0ff")
        global selected_index
        selected_index = index

    for i, row in enumerate(resident_rows):
        for j, value in enumerate(row[1:]):
            lbl = Label(data_frame, text=str(value), anchor="w", bg="white", width=[20, 30, 15, 10][j])
            lbl.grid(row=i, column=j, padx=5, pady=2, sticky="w")
            lbl.bind("<Button-1>", lambda e, index=i: on_row_click(e, index))

    global selected_index
    selected_index = None

def open_add_resident_window():
    def save_resident():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="brgy_profiling_system"
            )
            cursor = conn.cursor()
            query = "INSERT INTO residents (family_name, address, status) VALUES (%s, %s, %s)"
            cursor.execute(query, (family_name.get(), address.get(), status.get()))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "New resident added successfully.")
            add_window.destroy()
            refresh_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding resident: {err}")

    add_window = Toplevel()
    add_window.title("Add New Resident")
    add_window.geometry("400x250")

    family_name = StringVar()
    address = StringVar()
    status = StringVar(value="Active")

    tk.Label(add_window, text="Family Name").pack(pady=5)
    tk.Entry(add_window, textvariable=family_name, width=40).pack()

    tk.Label(add_window, text="Address").pack(pady=5)
    tk.Entry(add_window, textvariable=address, width=40).pack()

    tk.Label(add_window, text="Status").pack(pady=5)
    tk.OptionMenu(add_window, status, "Active", "Inactive").pack()

    tk.Button(add_window, text="Save", command=save_resident).pack(pady=10)


def open_edit_resident_window():
    if selected_index is None or selected_index >= len(resident_rows):
        messagebox.showwarning("Select Record", "Please select a resident to edit.")
        return

    resident = resident_rows[selected_index]
    resident_id = resident[0]

    def update_resident():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="brgy_profiling_system"
            )
            cursor = conn.cursor()
            query = "UPDATE residents SET family_name=%s, address=%s, status=%s WHERE id=%s"
            cursor.execute(query, (family_name.get(), address.get(), status.get(), resident_id))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Updated", "Resident information updated.")
            edit_window.destroy()
            refresh_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating resident: {err}")

    edit_window = Toplevel()
    edit_window.title("Edit Resident")
    edit_window.geometry("400x300")

    family_name = StringVar(value=resident[1])
    address = StringVar(value=resident[2])
    status = StringVar(value=resident[3])
    members = StringVar(value=resident[4])

    tk.Label(edit_window, text="Family Name").pack(pady=5)
    tk.Entry(edit_window, textvariable=family_name, width=40).pack()

    tk.Label(edit_window, text="Address").pack(pady=5)
    tk.Entry(edit_window, textvariable=address, width=40).pack()

    tk.Label(edit_window, text="Status").pack(pady=5)
    tk.OptionMenu(edit_window, status, "Active", "Inactive").pack()

    tk.Label(edit_window, text="Members").pack(pady=5)
    tk.Entry(edit_window, textvariable=members, width=40).pack()

    tk.Button(edit_window, text="Update", command=update_resident).pack(pady=10)

def open_resident_info(main_frame):
    global data_frame, resident_rows
    for widget in main_frame.winfo_children():
        widget.destroy()

    Label(main_frame, text="Residence Management", font=("Arial", 18, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20, 0))
    Label(main_frame, text="Manage resident information", font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
    Frame(main_frame, bg="#0c0c0c", height=2).pack(fill="x", padx=20, pady=10)

    # Controls
    top_frame = Frame(main_frame, bg="white")
    top_frame.pack(fill="x", padx=20, pady=10)

    # Filter Buttons
    Button(top_frame, text="All", width=8, command=lambda: refresh_data("All")).pack(side="left", padx=2)
    Button(top_frame, text="Active", width=8, command=lambda: refresh_data("Active")).pack(side="left", padx=2)
    Button(top_frame, text="Inactive", width=8, command=lambda: refresh_data("Inactive")).pack(side="left", padx=2)

    # Add New Resident Button (Restored)
    Button(top_frame, text="Add New Resident", bg="green", fg="white", width=15, command=open_add_resident_window).pack(side="left", padx=10)

    # Search field
    search_entry = Entry(top_frame, width=30)
    search_entry.pack(side="left", padx=10)

    def perform_search():
        query = search_entry.get()
        if query:
            rows = search_residents(query)
            refresh_data(custom_rows=rows)
        else:
            refresh_data()

    Button(top_frame, text="Search", width=10, command=perform_search).pack(side="left", padx=2)

    # Delete & Edit buttons
    def delete_selected():
        if selected_index is None or selected_index >= len(resident_rows):
            messagebox.showwarning("Select Record", "Please select a resident to delete.")
            return

        resident_id = resident_rows[selected_index][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this resident?")
        if confirm:
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="brgy_profiling_system"
                )
                cursor = conn.cursor()
                cursor.execute("DELETE FROM residents WHERE id = %s", (resident_id,))
                conn.commit()
                cursor.close()
                conn.close()
                refresh_data()
                messagebox.showinfo("Deleted", "Resident deleted.")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Delete failed: {err}")

    def search_residents(query):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="brgy_profiling_system"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id, family_name, address, status, members FROM residents WHERE family_name LIKE %s",
                           (f"%{query}%",))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching: {err}")
            return []

    Button(top_frame, text="Delete", bg="red", fg="white", width=10, command=delete_selected).pack(side="right", padx=(0, 5))
    Button(top_frame, text="Edit", bg="orange", fg="white", width=10, command=open_edit_resident_window).pack(side="right", padx=5)

    # Table headers
    header_frame = Frame(main_frame, bg="white")
    header_frame.pack(fill="x", padx=20)

    for i, title in enumerate(["Family Name", "Address", "Status", "Members"]):
        Label(header_frame, text=title, font=("Arial", 10, "bold"), width=[20, 24, 15, 10][i], anchor="w", bg="white").grid(row=0, column=i, padx=5, pady=5)

    # Table data
    data_frame = Frame(main_frame, bg="white", bd=1, relief="solid")
    data_frame.pack(fill="both", expand=True, padx=20, pady=10)

    refresh_data()
