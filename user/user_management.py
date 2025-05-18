import tkinter as tk
from tkinter import messagebox, StringVar, Label, Entry, Button, Frame, OptionMenu
from database.db_config import create_connection

user_rows = []
selected_user_index = None
COLUMN_WIDTHS = [25, 15]  # [Username Width, Role Width]

# Fetch users from the database
def fetch_users():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, username, role FROM users")
        rows = cursor.fetchall()
        connection.close()
        return rows
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching users: {e}")
        return []

# Refresh the displayed user data
def refresh_user_data():
    for widget in user_data_frame.winfo_children():
        widget.destroy()

    global user_rows
    user_rows = fetch_users()

    # Display users in a table
    for i, row in enumerate(user_rows):
        for j, value in enumerate(row[1:]):
            lbl = Label(user_data_frame, text=str(value), anchor="w", bg="white", width=COLUMN_WIDTHS[j])
            lbl.grid(row=i, column=j, padx=5, pady=2, sticky="w")
            lbl.bind("<Button-1>", lambda e, index=i: on_user_row_click(e, index))

# Handle row clicks to select a user
def on_user_row_click(event, index):
    global selected_user_index
    selected_user_index = index
    for widget in user_data_frame.winfo_children():
        widget.config(bg="white")
    row_widgets = user_data_frame.grid_slaves(row=index)
    for widget in row_widgets:
        widget.config(bg="#d1e0ff")

# Open the window to add a new user
def open_add_user_window():
    def save_user():
        try:
            connection = create_connection()
            cursor = connection.cursor()
            query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
            cursor.execute(query, (username.get(), password.get(), role.get()))
            connection.commit()
            connection.close()
            messagebox.showinfo("Success", "New user added successfully.")
            add_user_window.destroy()
            refresh_user_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding user: {e}")

    add_user_window = tk.Toplevel()
    add_user_window.title("Add New User")
    add_user_window.geometry("400x300")

    username = StringVar()
    password = StringVar()
    role = StringVar(value="admin")

    Label(add_user_window, text="Username").pack(pady=5)
    Entry(add_user_window, textvariable=username, width=40).pack()

    Label(add_user_window, text="Password").pack(pady=5)
    Entry(add_user_window, textvariable=password, width=40, show="*").pack()

    Label(add_user_window, text="Role").pack(pady=5)
    role_dropdown = OptionMenu(add_user_window, role, "admin", "employee")
    role_dropdown.pack(pady=5)

    Button(add_user_window, text="Save", command=save_user).pack(pady=10)

# Open the window to edit a selected user
def open_edit_user_window():
    if selected_user_index is None or selected_user_index >= len(user_rows):
        messagebox.showwarning("Select User", "Please select a user to edit.")
        return

    user = user_rows[selected_user_index]
    user_id = user[0]

    def update_user():
        try:
            connection = create_connection()
            cursor = connection.cursor()
            query = "UPDATE users SET username=%s, password=%s, role=%s WHERE id=%s"
            cursor.execute(query, (username.get(), password.get(), role.get(), user_id))
            connection.commit()
            connection.close()
            messagebox.showinfo("Updated", "User information updated.")
            edit_user_window.destroy()
            refresh_user_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating user: {e}")

    edit_user_window = tk.Toplevel()
    edit_user_window.title("Edit User")
    edit_user_window.geometry("400x300")

    username = StringVar(value=user[1])
    password = StringVar()
    role = StringVar(value=user[2])

    Label(edit_user_window, text="Username").pack(pady=5)
    Entry(edit_user_window, textvariable=username, width=40).pack()

    Label(edit_user_window, text="Password").pack(pady=5)
    Entry(edit_user_window, textvariable=password, width=40, show="*").pack()

    Label(edit_user_window, text="Role").pack(pady=5)
    role_dropdown = OptionMenu(edit_user_window, role, "admin", "employee")
    role_dropdown.pack(pady=5)

    Button(edit_user_window, text="Update", command=update_user).pack(pady=10)

# Delete selected user
def delete_user():
    if selected_user_index is None or selected_user_index >= len(user_rows):
        messagebox.showwarning("Select User", "Please select a user to delete.")
        return

    user_id = user_rows[selected_user_index][0]
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?")
    if confirm:
        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
            connection.close()
            messagebox.showinfo("Deleted", "User deleted.")
            refresh_user_data()
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {e}")

# Integrate the user management in the main content
def open_user_management(admin_window):
    global user_data_frame
    main_frame = admin_window  # Assuming admin_window is the main frame of the admin dashboard

    for widget in main_frame.winfo_children():
        widget.destroy()

    Label(main_frame, text="User Management", font=("Arial", 18, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20, 0))
    Label(main_frame, text="Manage user information", font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
    Frame(main_frame, bg="#0c0c0c", height=2).pack(fill="x", padx=20, pady=10)

    controls_frame = tk.Frame(main_frame, bg="white")
    controls_frame.pack(fill="x", padx=20, pady=10)

    Button(controls_frame, text="Add User", command=open_add_user_window, bg="green", fg="white", width=12).pack(side="left", padx=10)
    Button(controls_frame, text="Edit User", command=open_edit_user_window, bg="orange", fg="white", width=12).pack(side="left", padx=10)
    Button(controls_frame, text="Delete User", command=delete_user, bg="red", fg="white", width=12).pack(side="left", padx=10)

    header_frame = tk.Frame(main_frame, bg="white")
    header_frame.pack(fill="x", padx=20)

    headers = ["Username", "Role"]
    for i, title in enumerate(headers):
        Label(header_frame, text=title, font=("Arial", 10, "bold"), width=COLUMN_WIDTHS[i], anchor="w", bg="white").grid(row=0, column=i, padx=5, pady=5)

    user_data_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
    user_data_frame.pack(fill="both", expand=True, padx=20, pady=10)

    refresh_user_data()
