import tkinter as tk
from tkinter import messagebox
from database import connect_db

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Login")
        self.root.geometry("450x300")
        self.root.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self.root, text="LIBRARY MANAGEMENT SYSTEM", font=("Arial", 18, "bold"))
        title.pack(pady=25)
        frame = tk.Frame(self.root)
        frame.pack()
        tk.Label(frame, text="Username:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = tk.Entry(frame, width=25, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1)
        tk.Label(frame, text="Password:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(frame, width=25, show="*", font=("Arial", 12))
        self.password_entry.grid(row=1, column=1)
        tk.Button(self.root, text="LOGIN", width=15, font=("Arial", 12, "bold"), command=self.login).pack(pady=20)
        self.username_entry.focus()
        self.root.bind("<Return>", lambda event: self.login())

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning(
                "Login",
                "Please enter username and password."
            )
            return
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            AND password = ?
            """,
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            self.root.destroy()
            dashboard_root = tk.Tk()
            from dashboard import Dashboard
            Dashboard(dashboard_root)
            dashboard_root.mainloop()
        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )