import tkinter as tk


def open_emp_dashboard():
    # Create a new window for the employee dashboard
    emp_window = tk.Toplevel()
    emp_window.title("Employee Dashboard")

    # Set the window size (optional)
    emp_window.geometry("400x300")

    # Add a label to welcome the employee
    welcome_label = tk.Label(emp_window, text="Welcome to the Employee Dashboard!", font=("Arial", 14))
    welcome_label.pack(pady=20)

    # Add other features for the employee dashboard
    # For example, buttons for employee-specific functions
    btn_manage_residents = tk.Button(emp_window, text="Manage Residents",
                                     command=lambda: open_manage_residents(emp_window))
    btn_manage_residents.pack(pady=10)

    btn_view_reports = tk.Button(emp_window, text="View Reports", command=lambda: open_view_reports(emp_window))
    btn_view_reports.pack(pady=10)

    # Optionally, add a logout button to go back to the login page
    btn_logout = tk.Button(emp_window, text="Logout", command=emp_window.destroy)
    btn_logout.pack(pady=10)

    # Run the dashboard window loop
    emp_window.mainloop()


def open_manage_residents(window):
    # This function could open a new window or perform tasks related to managing residents
    manage_window = tk.Toplevel(window)
    manage_window.title("Manage Residents")
    tk.Label(manage_window, text="Manage resident data here").pack(pady=20)
    manage_window.mainloop()


def open_view_reports(window):
    # This function could open a new window or perform tasks related to viewing reports
    report_window = tk.Toplevel(window)
    report_window.title("View Reports")
    tk.Label(report_window, text="View reports here").pack(pady=20)
    report_window.mainloop()
