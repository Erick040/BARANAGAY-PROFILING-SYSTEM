import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector

def open_documents(main_frame):
    # Clear the frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Title
    tk.Label(main_frame, text="Documents Management", font=("Arial", 18, "bold"), bg="white").pack(anchor="w", pady=(0, 10))

    # Subtitle
    subtitle = tk.Label(main_frame, text="Request and manage official barangay documents", font=("Arial", 12), bg="white")
    subtitle.pack(anchor="w", pady=(0, 5))

    # Line below the subtitle
    line = tk.Canvas(main_frame, height=2, bg="#0A0A40", bd=0, highlightthickness=0)
    line.pack(fill="x", pady=(0, 10))

    # Document Card Generator
    def create_doc_card(parent, title, status, fee, image_path, row, col):
        frame = tk.Frame(parent, bg="white", highlightbackground="lightgray", highlightthickness=1, padx=15, pady=10)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        try:
            doc_img = Image.open(image_path).resize((50, 50), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(doc_img)
            image_label = tk.Label(frame, image=photo, bg="white")
            image_label.image = photo
        except:
            image_label = tk.Label(frame, text="No Image", bg="white")

        image_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")

        title_label = tk.Label(frame, text=title, font=("Arial", 16, "bold"), bg="white", anchor="w")
        title_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        status_label = tk.Label(frame, text=f"Status: {status}", font=("Arial", 14), fg="green", bg="white", anchor="w")
        status_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        fee_label = tk.Label(frame, text=f"Fee: ₱{fee}", font=("Arial", 14), bg="white", anchor="w")
        fee_label.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        def open_form(title):
            form = tk.Toplevel(main_frame)
            form.title(f"{title} Request Form")
            form.geometry("400x300")
            form.configure(bg="white")

            tk.Label(form, text=f"{title} Form", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

            form_frame = tk.Frame(form, bg="white")
            form_frame.pack(pady=10)

            tk.Label(form_frame, text="Full Name:", bg="white", anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=5)
            name_entry = tk.Entry(form_frame, width=30)
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(form_frame, text="Address:", bg="white", anchor="w").grid(row=1, column=0, sticky="w", padx=10, pady=5)
            address_entry = tk.Entry(form_frame, width=30)
            address_entry.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(form_frame, text="Purpose:", bg="white", anchor="w").grid(row=2, column=0, sticky="w", padx=10, pady=5)
            purpose_entry = tk.Entry(form_frame, width=30)
            purpose_entry.grid(row=2, column=1, padx=10, pady=5)

            def submit():
                name = name_entry.get()
                address = address_entry.get()
                purpose = purpose_entry.get()
                if name and address and purpose:
                    try:
                        conn = mysql.connector.connect(  # Direct MySQL connection
                            host="localhost",
                            user="root",
                            password="",
                            database="brgy_profiling_system"
                        )
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO document_requests (name, address, purpose, document_type)
                            VALUES (%s, %s, %s, %s)
                        """, (name, address, purpose, title))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo("Submitted", f"{title} request submitted successfully.")
                        form.destroy()
                    except mysql.connector.Error as err:
                        messagebox.showerror("Database Error", f"An error occurred: {err}")
                else:
                    messagebox.showwarning("Incomplete", "Please fill in all fields.")

            def cancel():
                form.destroy()

            # Submit and Cancel buttons
            button_frame = tk.Frame(form, bg="white")
            button_frame.pack(pady=10)

            submit_button = tk.Button(button_frame, text="Submit", bg="#4255FF", fg="white", width=20, command=submit)
            submit_button.pack(side="left", padx=10)

            cancel_button = tk.Button(button_frame, text="Cancel", bg="gray", fg="white", width=20, command=cancel)
            cancel_button.pack(side="right", padx=10)

        request_button = tk.Button(frame, text="Request", bg="#4255FF", fg="white", relief="flat", width=40,
                                   command=lambda: open_form(title))
        request_button.grid(row=3, column=0, columnspan=2, pady=3)

        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    # Manage Requests Button
    def open_manage_requests():
        form = tk.Toplevel(main_frame)
        form.title("Manage Requests")
        form.geometry("700x400")
        form.configure(bg="white")

        # Title for the manage requests form
        tk.Label(form, text="Manage Document Requests", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # Create a canvas with a vertical scrollbar
        canvas = tk.Canvas(form, bg="white")
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(form, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollable_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Fetch requests from the database
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="brgy_profiling_system"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT document_type, name, purpose, request_date FROM document_requests")
            requests = cursor.fetchall()
            conn.close()

            # Display request data in the table
            for row, request in enumerate(requests, start=1):
                for col, value in enumerate(request):
                    tk.Label(scrollable_frame, text=value, font=("Arial", 12), bg="white").grid(row=row, column=col, padx=10, pady=5)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"An error occurred: {err}")

        # Update scroll region
        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    # Manage Requests Button
    manage_requests_button = tk.Button(main_frame, text="Manage Requests", bg="#4255FF", fg="white", width=20,
                                       command=open_manage_requests)
    manage_requests_button.pack(pady=10)

    # Container for documents
    docs_frame = tk.Frame(main_frame, bg="white")
    docs_frame.pack(fill="both", expand=True)

    documents = [
        ("Barangay Clearance", "available", 100, "assets/icons/clip-icon.jpg"),
        ("Certificate of Residency", "available", 75, "assets/icons/cert-icon.jpg"),
        ("Business Permit", "available", 500, "assets/icons/docs-icon.jpg"),
        ("Barangay ID", "available", 150, "assets/icons/id-icon.jpg"),
    ]

    for i in range(2):
        docs_frame.grid_columnconfigure(i, weight=1, uniform="equal")
        docs_frame.grid_rowconfigure(i, weight=1, uniform="equal")

    for i, doc in enumerate(documents):
        row = i // 2
        col = i % 2
        create_doc_card(docs_frame, *doc, row=row, col=col)
