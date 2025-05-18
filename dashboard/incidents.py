import tkinter as tk
from tkinter import Frame, Label, Button, Entry, Toplevel, Text, Scrollbar, Canvas, messagebox
from tkinter import ttk
import mysql.connector
from datetime import datetime

incident_data_frame = None
incident_canvas = None
canvas_frame = None
scrollbar = None
search_entry = None
current_filter = None

def fetch_incidents(filter_status=None, search_term=None):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="brgy_profiling_system"
        )
        cursor = conn.cursor()
        query = "SELECT id, incident_type, date_reported, description, location, status FROM incidents"
        values = []

        if filter_status:
            query += " WHERE status = %s"
            values.append(filter_status)

        if search_term:
            if "WHERE" in query:
                query += " AND (incident_type LIKE %s OR location LIKE %s)"
            else:
                query += " WHERE (incident_type LIKE %s OR location LIKE %s)"
            values.extend([f"%{search_term}%", f"%{search_term}%"])

        cursor.execute(query, values)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error fetching incidents: {err}")
        return []

def view_description(description):
    window = Toplevel()
    window.title("Incident Description")
    window.geometry("400x300")

    Label(window, text="Description", font=("Arial", 14, "bold")).pack(pady=10)
    text = Text(window, wrap="word", font=("Arial", 11))
    text.insert("1.0", description)
    text.config(state="disabled")
    text.pack(expand=True, fill="both", padx=10, pady=10)

def edit_incident(incident_id):
    def save_edited_incident():
        new_type = entry_type.get()
        new_location = entry_location.get()
        new_description = text_description.get("1.0", "end").strip()
        new_status = combobox_status.get()

        if not all([new_type, new_location, new_description, new_status]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="brgy_profiling_system"
            )
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE incidents 
                SET incident_type = %s, location = %s, description = %s, status = %s 
                WHERE id = %s
            """, (new_type, new_location, new_description, new_status, incident_id))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Incident updated successfully.")
            edit_form.destroy()
            refresh_incident_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error updating incident: {err}")

    # Fetch the current incident details
    incidents = fetch_incidents()
    current_incident = next((row for row in incidents if row[0] == incident_id), None)

    if current_incident:
        inc_type, date_reported, description, location, status = current_incident[1:]

        edit_form = Toplevel()
        edit_form.title(f"Edit Incident ID {incident_id}")
        edit_form.geometry("400x450")

        Label(edit_form, text="Incident Type").pack(anchor="w", padx=10, pady=5)
        entry_type = Entry(edit_form, width=40)
        entry_type.insert(0, inc_type)
        entry_type.pack(padx=10)

        Label(edit_form, text="Location").pack(anchor="w", padx=10, pady=5)
        entry_location = Entry(edit_form, width=40)
        entry_location.insert(0, location)
        entry_location.pack(padx=10)

        Label(edit_form, text="Description").pack(anchor="w", padx=10, pady=5)
        text_description = Text(edit_form, height=8, wrap="word")
        text_description.insert("1.0", description)
        text_description.pack(padx=10, pady=(0, 10), fill="x")

        Label(edit_form, text="Status").pack(anchor="w", padx=10, pady=5)
        combobox_status = ttk.Combobox(edit_form, values=["Unresolved", "Resolved"], width=40)
        combobox_status.set(status)
        combobox_status.pack(padx=10)

        Button(edit_form, text="Save Changes", command=save_edited_incident, bg="#28a745", fg="white").pack(pady=10)

def delete_incident(incident_id):
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this incident?"):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="brgy_profiling_system"
            )
            cursor = conn.cursor()
            cursor.execute("DELETE FROM incidents WHERE id = %s", (incident_id,))
            conn.commit()
            cursor.close()
            conn.close()
            refresh_incident_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error deleting incident: {err}")

def refresh_incident_data():
    global current_filter
    incidents = fetch_incidents(filter_status=current_filter, search_term=search_entry.get())

    for widget in canvas_frame.winfo_children():
        widget.destroy()

    for i, row in enumerate(incidents):
        inc_id, inc_type, date_reported, description, location, status = row
        row_bg = "#f9f9f9" if i % 2 == 0 else "white"

        Label(canvas_frame, text=inc_type, width=20, anchor="w", bg=row_bg).grid(row=i, column=0, padx=5, pady=4, sticky="w")
        Label(canvas_frame, text=date_reported, width=15, anchor="w", bg=row_bg).grid(row=i, column=1, padx=5, pady=4, sticky="w")
        Button(canvas_frame, text="View", bg="#007bff", fg="white", width=6, command=lambda d=description: view_description(d)).grid(row=i, column=2, padx=5, pady=4, sticky="w")
        Label(canvas_frame, text=location, width=25, anchor="w", bg=row_bg).grid(row=i, column=3, padx=5, pady=4, sticky="w")
        Label(canvas_frame, text=status, width=15, anchor="w", bg=row_bg).grid(row=i, column=4, padx=5, pady=4, sticky="w")
        Button(canvas_frame, text="Edit", bg="#ffc107", fg="black", width=6, command=lambda i=inc_id: edit_incident(i)).grid(row=i, column=5, padx=5, pady=4, sticky="w")
        Button(canvas_frame, text="Delete", bg="#dc3545", fg="white", width=6, command=lambda i=inc_id: delete_incident(i)).grid(row=i, column=6, padx=5, pady=4, sticky="w")

def add_new_incident():
    def save_incident():
        incident_type = entry_type.get()
        date_reported = entry_date.get()
        location = entry_location.get()
        description = text_description.get("1.0", "end").strip()
        status = "Unresolved"

        if not all([incident_type, date_reported, location, description]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="brgy_profiling_system"
            )
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO incidents (incident_type, date_reported, location, status, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (incident_type, date_reported, location, status, description))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Incident added successfully.")
            form.destroy()
            refresh_incident_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding incident: {err}")

    form = Toplevel()
    form.title("Add New Incident")
    form.geometry("400x450")

    Label(form, text="Incident Type").pack(anchor="w", padx=10, pady=5)
    entry_type = Entry(form, width=40)
    entry_type.pack(padx=10)

    Label(form, text="Date Reported (YYYY-MM-DD)").pack(anchor="w", padx=10, pady=5)
    entry_date = Entry(form, width=40)
    entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
    entry_date.pack(padx=10)

    Label(form, text="Location").pack(anchor="w", padx=10, pady=5)
    entry_location = Entry(form, width=40)
    entry_location.pack(padx=10)

    Label(form, text="Description").pack(anchor="w", padx=10, pady=5)
    text_description = Text(form, height=8, wrap="word")
    text_description.pack(padx=10, pady=(0, 10), fill="x")

    Button(form, text="Save Incident", command=save_incident, bg="#28a745", fg="white").pack(pady=10)

def open_incidents(main_frame):
    global incident_data_frame, incident_canvas, canvas_frame, scrollbar, search_entry, current_filter
    current_filter = None

    for widget in main_frame.winfo_children():
        widget.destroy()

    Label(main_frame, text="Incidents", font=("Arial", 18, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20, 0))
    Label(main_frame, text="Manage reported incidents", font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
    Frame(main_frame, bg="#0c0c0c", height=2).pack(fill="x", padx=20, pady=10)

    top_frame = Frame(main_frame, bg="white")
    top_frame.pack(fill="x", padx=20, pady=5)

    Button(top_frame, text="Add New Incident", command=add_new_incident, bg="#007bff", fg="white").pack(side="left")

    search_entry = Entry(top_frame, width=30)
    search_entry.pack(side="left", padx=(10, 5))
    Button(top_frame, text="Search", command=refresh_incident_data).pack(side="left")

    Button(top_frame, text="Unresolved", command=lambda: set_filter("Unresolved"), bg="#ffc107").pack(side="left", padx=5)
    Button(top_frame, text="Resolved", command=lambda: set_filter("Resolved"), bg="#28a745", fg="white").pack(side="left")

    header_frame = Frame(main_frame, bg="white")
    header_frame.pack(fill="x", padx=20)

    headers = ["Type", "Date", "Description", "Location", "Status", "Actions", ""]
    widths = [20, 10, 13, 16, 15, 0, 0]
    for i, (title, width) in enumerate(zip(headers, widths)):
        Label(header_frame, text=title, font=("Arial", 10, "bold"), width=width, anchor="w", bg="white").grid(row=0, column=i, padx=5, pady=5, sticky="w")

    # Scrollable incident list
    container = Frame(main_frame)
    container.pack(fill="both", expand=True, padx=20, pady=10)

    incident_canvas = Canvas(container, bg="white")
    scrollbar = Scrollbar(container, orient="vertical", command=incident_canvas.yview)
    incident_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    incident_canvas.pack(side="left", fill="both", expand=True)

    canvas_frame = Frame(incident_canvas, bg="white")
    incident_canvas.create_window((0, 0), window=canvas_frame, anchor="nw")

    canvas_frame.bind("<Configure>", lambda e: incident_canvas.configure(scrollregion=incident_canvas.bbox("all")))

    refresh_incident_data()

def set_filter(status):
    global current_filter
    current_filter = status
    refresh_incident_data()
