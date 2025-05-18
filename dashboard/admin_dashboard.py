import tkinter as tk
from tkinter import Canvas, Label, Button, Frame
from PIL import Image, ImageTk
import subprocess
from dashboard.dashboard_view import open_dashboard
from dashboard.resident_info_view import open_resident_info
from dashboard.household_data import open_household_data
from dashboard.documents import open_documents
from dashboard.incidents import open_incidents
from user.user_management import open_user_management

logo_photo = None

def sign_out(admin_window, root):
    admin_window.destroy()
    root.destroy()  # Also destroy root window to cleanly exit
    subprocess.run(["python", "login_page.py"])

def open_admin_dashboard(root):
    admin_window = tk.Toplevel(root)
    admin_window.title("Barangay System Admin Dashboard")
    admin_window.geometry("1100x600")
    admin_window.config(bg="white")

    # Header
    header = Frame(admin_window, bg="#0A0A40", height=50)
    header.pack(side="top", fill="x")
    header_title = Label(header, text="BARANGAY PROFILING SYSTEM", font=("Arial", 14, "bold"),
                         bg="#0A0A40", fg="white")
    header_title.pack(pady=10)

    # Sidebar
    sidebar = Frame(admin_window, width=200, bg="#0A0A40")
    sidebar.pack(side="left", fill="y")

    logo_label = Label(sidebar, text="BARANGAY MINTAL", fg="white", bg="#0A0A40", font=("Arial", 12, "bold"))
    logo_label.pack(pady=(20, 10))

    try:
        global logo_photo
        logo_image = Image.open("C:/Users/Ellen/Downloads/BRG_Logo.png")
        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS
        logo_image = logo_image.resize((190, 190), resample_filter)
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_widget = Label(sidebar, image=logo_photo, bg="#0A0A40")
        logo_widget.pack(pady=(0, 20))
    except Exception as e:
        print(f"Error loading logo: {e}")

    # Main Content Area
    global main_frame
    main_frame = Frame(admin_window, bg="white")
    main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    def clear_main_frame():
        for widget in main_frame.winfo_children():
            widget.destroy()

    # Buttons
    nav_buttons = [
        ("Dashboard", open_dashboard),
        ("Resident Info", open_resident_info),
        ("Household Data", open_household_data),
        ("Documents", open_documents),
        ("Incidents", open_incidents),
        ("User Management", open_user_management)
    ]

    for name, func in nav_buttons:
        btn = Button(sidebar, text=name, font=("Arial", 10), bg="white", fg="black",
                     relief="flat", width=20,
                     command=lambda f=func: (clear_main_frame(), f(main_frame)))
        btn.pack(pady=5)

    # Sign out button
    signout_btn = Button(sidebar, text="Sign out", command=lambda: sign_out(admin_window, root),
                         font=("Arial", 10, "underline"), bg="#0A0A40", fg="white",
                         relief="flat", anchor="w", padx=10)
    signout_btn.pack(side="bottom", fill="x", padx=10, pady=20)

    # Load default page
    open_dashboard(main_frame)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window immediately
    open_admin_dashboard(root)
    root.mainloop()
