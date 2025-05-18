import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import mysql.connector

# Import your admin dashboard function here
from dashboard.admin_dashboard import open_admin_dashboard

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="brgy_profiling_system"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error connecting to MySQL:\n{err}")
        return None

def create_rounded_frame(width, height, radius, color):
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=color)
    return ImageTk.PhotoImage(img)

def login_function():
    username = username_entry.get()
    password = password_entry.get()

    connection = connect_to_db()
    if connection is None:
        return

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        role = user[3]  # Adjust index if needed

        if role == 'admin':
            # Hide the login window instead of destroying it
            root.withdraw()
            open_admin_dashboard(root)  # Pass root to admin dashboard
        elif role == 'employee':
            messagebox.showinfo("Login Success", "Employee dashboard placeholder.")
        else:
            messagebox.showerror("Unknown Role", "Unknown role assigned to this user.")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

    cursor.close()
    connection.close()

# Tkinter window setup
root = tk.Tk()
root.title("Login - Barangay Profiling System")
root.geometry("900x500")
root.resizable(False, False)

# Background Image
bg_image_path = "C:/Users/Ellen/Downloads/backgroundbrg.webp"
bg_image = Image.open(bg_image_path).resize((900, 600), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Title
tk.Label(root, text="BARANGAY PROFILING SYSTEM", font=("Arial", 24, "bold"),
         bg="#102362", fg="white").place(relx=0.5, rely=0.1, anchor="center")

# Rounded background for form
rounded_bg = create_rounded_frame(700, 300, 20, "#102362")
main_canvas = tk.Canvas(root, width=700, height=300, bg="white", bd=0, highlightthickness=0)
main_canvas.place(relx=0.5, rely=0.5, anchor="center")
main_canvas.create_image(0, 0, image=rounded_bg, anchor="nw")
main_canvas.image = rounded_bg

# Left form
form_frame = tk.Frame(root, bg="#102362", width=350, height=300)
form_frame.place(relx=0.25, rely=0.5, anchor="center")

tk.Label(form_frame, text="BARANGAY MINTAL", font=("Arial", 16, "bold"),
         bg="#102362", fg="white").place(relx=0.55, rely=0.1, anchor="center")

tk.Label(form_frame, text="Username", font=("Arial", 14), bg="#102362", fg="white").place(x=30, y=60)
username_entry = tk.Entry(form_frame, font=("Arial", 14), width=28)
username_entry.place(x=30, y=90)

tk.Label(form_frame, text="Password", font=("Arial", 14), bg="#102362", fg="white").place(x=30, y=130)
password_entry = tk.Entry(form_frame, font=("Arial", 14), width=28, show="*")
password_entry.place(x=30, y=160)

tk.Button(form_frame, text="Login", font=("Arial", 14), bg='blue', fg='white',
          command=login_function).place(relx=0.5, y=230, anchor="center")

# Right logo
logo_frame = tk.Frame(root, bg='#102362', width=350, height=300)
logo_frame.place(relx=0.75, rely=0.5, anchor="center")

logo_path = "C:/Users/Ellen/Downloads/BRG_Logo.png"
logo_image = Image.open(logo_path).resize((300, 300), Image.Resampling.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(logo_frame, image=logo_photo, bg='#102362')
logo_label.place(relx=0.5, rely=0.5, anchor='center')
logo_label.image = logo_photo

root.mainloop()
