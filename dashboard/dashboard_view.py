import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
import mysql.connector

def fetch_dashboard_data():
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host="localhost",            # Localhost for local MySQL server
            user="root",            # Replace with your MySQL username
            password="",    # Replace with your MySQL password
            database="brgy_profiling_system"
        )

        cursor = conn.cursor()

        # Total Residents
        cursor.execute("SELECT COUNT(*) FROM residents WHERE status = 'Active'")
        total_residents = cursor.fetchone()[0]

        # Male Residents
        cursor.execute("SELECT COUNT(*) FROM individuals WHERE gender = 'Male'")
        male_residents = cursor.fetchone()[0]

        # Female Residents
        cursor.execute("SELECT COUNT(*) FROM individuals WHERE gender = 'Female'")
        female_residents = cursor.fetchone()[0]

        # Total Households (assuming it's equivalent to residents)
        cursor.execute("SELECT COUNT(*) FROM residents")
        total_households = cursor.fetchone()[0]

        # Active Incidents
        cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'Unresolved'")
        total_incidents = cursor.fetchone()[0]

        # Debugging: Print fetched data
        print(f"Total Residents: {total_residents}")
        print(f"Male Residents: {male_residents}")
        print(f"Female Residents: {female_residents}")
        print(f"Total Households: {total_households}")
        print(f"Total Unresolved Incidents: {total_incidents}")

        # Return the fetched data
        return {
            "total_residents": total_residents,
            "male_residents": male_residents,
            "female_residents": female_residents,
            "total_households": total_households,
            "total_incidents": total_incidents
        }

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return {}

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def open_dashboard(main_frame):
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Title
    tk.Label(main_frame, text="Barangay Resident Demographics", font=("Arial", 18, "bold"), bg="white").pack(anchor="w")
    tk.Label(main_frame, text="Overview of the current population and household data", font=("Arial", 12),
             bg="white").pack(anchor="w", pady=(0, 20))

    # Line separator
    line_canvas = Canvas(main_frame, width=960, height=2, bg="white", highlightthickness=0)
    line_canvas.create_line(0, 1, 960, 1, fill="#0A0A40", width=2)
    line_canvas.pack(pady=(0, 20))

    # Fetch data from the database
    data = fetch_dashboard_data()

    # Check if data is empty or not
    if not data:
        print("No data fetched from the database.")
        return

    # Stats frame
    stats_frame = tk.Frame(main_frame, bg="white")
    stats_frame.pack(anchor="w", pady=10)

    stats = [
        ("Total Resident", data.get("total_residents", 0), "#2e7d32"),   # changed to green
        ("Male", data.get("male_residents", 0), "#2166c1"),              # changed to blue
        ("Female", data.get("female_residents", 0), "#b71c1c"),
        ("Household", data.get("total_households", 0), "#1c1c2e"),
        ("Unresolved Incidents", data.get("total_incidents", 0), "#FF5722")
    ]

    for i, (label, value, color) in enumerate(stats):
        stat_box = tk.Frame(stats_frame, bg=color, padx=10, pady=5)
        tk.Label(stat_box, text=label, font=("Arial", 10), fg="white", bg=color).pack()
        tk.Label(stat_box, text=value, font=("Arial", 14, "bold"), fg="white", bg=color).pack()
        stat_box.grid(row=0, column=i, padx=20, pady=10, sticky="ew")

    for i in range(5):
        stats_frame.grid_columnconfigure(i, weight=1)

    # Charts frame
    charts_frame = tk.Frame(main_frame, bg="white")
    charts_frame.pack(fill="both", expand=True, pady=30)

    # Gender distribution (Pie Chart)
    gender_canvas = Canvas(charts_frame, width=300, height=300, bg="white", highlightthickness=0)
    gender_canvas.create_text(150, 20, text="Gender Distribution", font=("Arial", 14, "bold"))
    gender_canvas.create_arc(50, 50, 250, 250, start=0, extent=208, fill="#2166c1")   # Male: Blue
    gender_canvas.create_arc(50, 50, 250, 250, start=208, extent=152, fill="#8B0000") # Female: Dark Red
    gender_canvas.pack(side="left", padx=30)

    # Age group breakdown (Bar Graph)
    age_canvas = Canvas(charts_frame, width=400, height=300, bg="white", highlightthickness=0)
    age_canvas.create_text(200, 20, text="Age Group Breakdown", font=("Arial", 14, "bold"))

    age_groups = {"0-17": 300, "17-35": 800, "36-59": 250, "60+": 150}
    x_start = 50
    bar_width = 50

    for age, height in age_groups.items():
        scaled_height = height // 4
        top_y = 250 - scaled_height
        # Draw bar
        age_canvas.create_rectangle(
            x_start, top_y, x_start + bar_width, 250,
            fill="#90ee90", outline=""
        )
        # Draw label below bar
        age_canvas.create_text(
            x_start + bar_width // 2, 260, text=age, anchor="n", font=("Arial", 10, "bold")
        )
        # Draw value *inside* the bar
        age_canvas.create_text(
            x_start + bar_width // 2, top_y + 10,  # 10 pixels down from top of bar
            text=str(height), anchor="n", font=("Arial", 10), fill="black"
        )
        x_start += 100

    age_canvas.pack(side="right", padx=30)
