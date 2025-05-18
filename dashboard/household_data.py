import tkinter as tk
from tkinter import Frame, Label, Button, Entry, messagebox, Toplevel
import mysql.connector
from datetime import datetime
from tkinter import ttk  # Add this to your imports at the top

household_data_frame = None
household_rows = []
selected_household_index = None

# Fetch household summary data (including Last Update)
def fetch_household_summary():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="brgy_profiling_system"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, family_name, address, members, status, last_updated FROM residents")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching data: {err}")
        return []

# Function to search households by family name or address
def search_households(query):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="brgy_profiling_system"
        )
        cursor = conn.cursor()
        # Search by family_name or address (you can expand this query to include other fields)
        cursor.execute("""SELECT id, family_name, address, members, status, last_updated 
                          FROM residents 
                          WHERE family_name LIKE %s OR address LIKE %s""",
                       ('%' + query + '%', '%' + query + '%'))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error searching households: {err}")
        return []


# View members of a selected household (linked to residents.id)
def view_household_members(resident_id):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="brgy_profiling_system"
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, first_name, last_name, age, gender, occupation, status 
            FROM individuals WHERE resident_id = %s
        """, (resident_id,))
        members = cursor.fetchall()
        cursor.close()
        conn.close()

        members_window = Toplevel()
        members_window.title("Household Members")
        members_window.geometry("750x400")

        if not members:
            Label(members_window, text="No members found.", font=("Arial", 12)).pack(pady=20)
            return

        Label(members_window, text="Household Members", font=("Arial", 14, "bold")).pack(pady=10)

        # Column headers
        header_frame = Frame(members_window)
        header_frame.pack(fill="x", padx=10)
        headers = ["Full Name", "Age", "Gender", "Occupation", "Status", "Action"]
        widths = [25, 5, 10, 20, 10, 10]
        for i, (h, w) in enumerate(zip(headers, widths)):
            Label(header_frame, text=h, font=("Arial", 10, "bold"), width=w, anchor="w").grid(row=0, column=i, padx=3)

        for i, member in enumerate(members):
            member_id, first_name, last_name, age, gender, occupation, status = member
            full_name = f"{first_name} {last_name}"

            row_frame = Frame(members_window)
            row_frame.pack(fill="x", padx=10, pady=1)

            Label(row_frame, text=full_name, width=25, anchor="w").grid(row=0, column=0, padx=3)
            Label(row_frame, text=str(age), width=5, anchor="w").grid(row=0, column=1, padx=3)
            Label(row_frame, text=gender, width=10, anchor="w").grid(row=0, column=2, padx=3)
            Label(row_frame, text=occupation, width=20, anchor="w").grid(row=0, column=3, padx=3)
            Label(row_frame, text=status, width=10, anchor="w").grid(row=0, column=4, padx=3)

            Button(row_frame, text="Delete", bg="red", fg="white",
                   command=lambda mid=member_id: delete_member(mid, members_window, resident_id)).grid(row=0, column=5, padx=3)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching members: {err}")


def delete_member(member_id, window, resident_id):
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this member?")
    if not confirm:
        return

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="brgy_profiling_system"
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM individuals WHERE id = %s", (member_id,))
        conn.commit()
        cursor.close()
        conn.close()

        messagebox.showinfo("Success", "Member deleted successfully.")
        window.destroy()
        view_household_members(resident_id)  # Reopen the list to reflect changes

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error deleting member: {err}")




# Function to edit household information and add members
def edit_household_members(resident_id):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="brgy_profiling_system"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT family_name, address, status FROM residents WHERE id = %s", (resident_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            family_name, address, status = row
            edit_window = Toplevel()
            edit_window.title("Edit Household")
            edit_window.geometry("400x450")

            Label(edit_window, text="Edit Household Information", font=("Arial", 14, "bold")).pack(pady=10)

            family_name_entry = Entry(edit_window, width=30)
            family_name_entry.insert(0, family_name)
            family_name_entry.pack(pady=5)

            address_entry = Entry(edit_window, width=30)
            address_entry.insert(0, address)
            address_entry.pack(pady=5)

            status_entry = Entry(edit_window, width=30)
            status_entry.insert(0, status)
            status_entry.pack(pady=5)

            # Function to add a new member
            def add_new_member():
                add_member_window = Toplevel()
                add_member_window.title("Add New Member")
                add_member_window.geometry("300x400")

                Label(add_member_window, text="Add New Member", font=("Arial", 14, "bold")).pack(pady=10)

                first_name_entry = Entry(add_member_window, width=30)
                first_name_entry.pack(pady=5)
                first_name_entry.insert(0, "First Name")

                last_name_entry = Entry(add_member_window, width=30)
                last_name_entry.pack(pady=5)
                last_name_entry.insert(0, "Last Name")

                age_entry = Entry(add_member_window, width=30)
                age_entry.pack(pady=5)
                age_entry.insert(0, "Age")

                gender_entry = Entry(add_member_window, width=30)
                gender_entry.pack(pady=5)
                gender_entry.insert(0, "Gender")

                occupation_entry = Entry(add_member_window, width=30)
                occupation_entry.pack(pady=5)
                occupation_entry.insert(0, "Occupation")

                Label(add_member_window, text="Status").pack(pady=(5, 0))
                status_combobox = ttk.Combobox(add_member_window, values=["Alive", "Deceased"], state="readonly", width=28)
                status_combobox.current(0)
                status_combobox.pack(pady=5)

                def save_new_member():
                    first_name = first_name_entry.get()
                    last_name = last_name_entry.get()
                    age = age_entry.get()
                    gender = gender_entry.get()
                    occupation = occupation_entry.get()
                    status = status_combobox.get()

                    if all([first_name, last_name, age, gender, occupation, status]):
                        try:
                            conn = mysql.connector.connect(
                                host="localhost",
                                user="root",
                                password="",
                                database="brgy_profiling_system"
                            )
                            cursor = conn.cursor()
                            cursor.execute("""
                                INSERT INTO individuals (first_name, last_name, age, gender, occupation, status, resident_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (first_name, last_name, age, gender, occupation, status, resident_id))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            messagebox.showinfo("Success", "New member added successfully.")
                            add_member_window.destroy()
                            refresh_household_data()
                        except mysql.connector.Error as err:
                            messagebox.showerror("Database Error", f"Error adding member: {err}")
                    else:
                        messagebox.showwarning("Incomplete", "Please fill in all fields.")

                Button(add_member_window, text="Save Member", bg="#28a745", fg="white", command=save_new_member).pack(pady=10)
                Button(add_member_window, text="Cancel", bg="gray", fg="white", command=add_member_window.destroy).pack(pady=5)

            # Add Member Button
            add_member_button = Button(edit_window, text="Add Member", bg="#007bff", fg="white", command=add_new_member)
            add_member_button.pack(pady=10)

            # Save changes to household information
            def save_changes():
                updated_family_name = family_name_entry.get()
                updated_address = address_entry.get()
                updated_status = status_entry.get()

                if updated_family_name and updated_address and updated_status:
                    try:
                        conn = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
                            database="brgy_profiling_system"
                        )
                        cursor = conn.cursor()
                        cursor.execute("""UPDATE residents SET family_name = %s, address = %s, status = %s
                                          WHERE id = %s""",
                                       (updated_family_name, updated_address, updated_status, resident_id))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        messagebox.showinfo("Success", "Household information updated successfully.")
                        edit_window.destroy()
                        refresh_household_data()
                    except mysql.connector.Error as err:
                        messagebox.showerror("Database Error", f"Error updating data: {err}")
                else:
                    messagebox.showwarning("Incomplete", "Please fill in all fields.")

            save_button = Button(edit_window, text="Save Changes", bg="#28a745", fg="white", command=save_changes)
            save_button.pack(pady=10)

            cancel_button = Button(edit_window, text="Cancel", bg="gray", fg="white", command=edit_window.destroy)
            cancel_button.pack(pady=5)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching data: {err}")



# Refresh displayed household data
def refresh_household_data(status_filter=None, custom_rows=None):
    for widget in household_data_frame.winfo_children():
        widget.destroy()

    global household_rows
    all_rows = custom_rows if custom_rows is not None else fetch_household_summary()
    if status_filter and status_filter != "All":
        household_rows = [row for row in all_rows if row[4] == status_filter]
    else:
        household_rows = all_rows

    for i, row in enumerate(household_rows):
        if len(row) < 6:
            print(f"Skipping incomplete row: {row}")
            continue  # Skip this row if it doesn't have enough columns

        resident_id = row[0]
        family_name, address, status = row[1], row[2], row[4]

        last_updated = row[5] if len(row) > 5 and row[5] else "Not Available"
        last_updated = last_updated.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_updated, datetime) else last_updated

        Label(household_data_frame, text=family_name, anchor="w", bg="white", width=20).grid(row=i, column=0, padx=5, pady=2, sticky="w")
        Label(household_data_frame, text=address, anchor="w", bg="white", width=30).grid(row=i, column=1, padx=5, pady=2, sticky="w")
        Label(household_data_frame, text=status, anchor="w", bg="white", width=12).grid(row=i, column=2, padx=5, pady=2, sticky="w")
        Label(household_data_frame, text=last_updated, anchor="w", bg="white", width=18).grid(row=i, column=3, padx=5, pady=2, sticky="w")

        btn_view = Button(household_data_frame, text="View", bg="#007bff", fg="white", width=6, command=lambda rid=resident_id: view_household_members(rid))
        btn_view.grid(row=i, column=4, padx=(5, 2), pady=2)

        btn_edit = Button(household_data_frame, text="Edit", bg="#f0ad4e", fg="white", width=6, command=lambda rid=resident_id: edit_household_members(rid))
        btn_edit.grid(row=i, column=5, padx=(2, 5), pady=2)

    global selected_household_index
    selected_household_index = None

# Open household data section with scroll bar and new spacings
def open_household_data(main_frame):
    global household_data_frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    Label(main_frame, text="Household Data", font=("Arial", 18, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20, 0))
    Label(main_frame, text="Manage household information", font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
    Frame(main_frame, bg="#0c0c0c", height=2).pack(fill="x", padx=20, pady=10)

    top_frame = Frame(main_frame, bg="white")
    top_frame.pack(fill="x", padx=20, pady=10)

    Button(top_frame, text="All", width=8, command=lambda: refresh_household_data("All")).pack(side="left", padx=2)
    Button(top_frame, text="Active", width=8, command=lambda: refresh_household_data("Active")).pack(side="left", padx=2)
    Button(top_frame, text="Inactive", width=8, command=lambda: refresh_household_data("Inactive")).pack(side="left", padx=2)

    search_entry = Entry(top_frame, width=30)
    search_entry.pack(side="left", padx=10)

    def perform_search():
        query = search_entry.get()
        if query:
            rows = search_households(query)
            refresh_household_data(custom_rows=rows)
        else:
            refresh_household_data()

    Button(top_frame, text="Search", width=10, command=perform_search).pack(side="left", padx=2)

    header_frame = Frame(main_frame, bg="white")
    header_frame.pack(fill="x", padx=20)

    headers = ["Household Name", "Address", "Status", "Last Updated", "Members"]
    widths = [22, 21, 12, 18, 15, 12]  # Adjusted width for the Last Updated column
    for i, (title, width) in enumerate(zip(headers, widths)):
        Label(header_frame, text=title, font=("Arial", 10, "bold"), width=width, anchor="w", bg="white").grid(row=0, column=i, padx=5, pady=5)

    household_data_frame = Frame(main_frame, bg="white")
    household_data_frame.pack(fill="both", expand=True, padx=20, pady=10)

    canvas = tk.Canvas(household_data_frame)
    scrollbar = tk.Scrollbar(household_data_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollbar.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)
    scrollable_frame.update_idletasks()

    canvas.config(scrollregion=canvas.bbox("all"))
    refresh_household_data()  # Load data initially
