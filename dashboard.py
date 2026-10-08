import tkinter as tk
from tkinter import messagebox
from database import connect_db

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1000x600")
        self.create_menu()
        self.create_dashboard()
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Dashboard", command=self.create_dashboard)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)
        management_menu = tk.Menu(menu_bar, tearoff=0)
        management_menu.add_command(label="Books", command=self.open_books)
        management_menu.add_command(label="Members", command=self.open_members)
        management_menu.add_command(label="Issue Book", command=self.open_issue)
        management_menu.add_command(label="Return Book", command=self.open_return)
        menu_bar.add_cascade(label="Management", menu=management_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menu_bar)

    def create_dashboard(self):
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()
        title = tk.Label(self.root, text="LIBRARY MANAGEMENT SYSTEM", font=("Arial", 26, "bold"))
        title.pack(pady=30)
        tk.Label(self.root, text="Dashboard", font=("Arial", 18)).pack()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM books"
        )
        total_books = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM books"
        )
        total_copies = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COALESCE(SUM(available), 0) FROM books"
        )
        available = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM members"
        )
        members = cursor.fetchone()[0]
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM transactions
            WHERE status = 'Issued'
            """
        )
        issued = cursor.fetchone()[0]
        conn.close()

        frame = tk.Frame(self.root)
        frame.pack(pady=40)
        statistics = [
            ("Book Titles", total_books),
            ("Total Copies", total_copies),
            ("Available", available),
            ("Members", members),
            ("Issued", issued)
        ]
        for i, (name, value) in enumerate(statistics):
            card = tk.Frame(frame, width=160, height=120, relief="ridge", borderwidth=2)
            card.grid(row=0, column=i, padx=8)
            card.pack_propagate(False)
            tk.Label(card, text=str(value), font=("Arial", 25, "bold")).pack(pady=15)
            tk.Label(card, text=name, font=("Arial", 11)).pack()
        button_frame = tk.Frame(self.root)
        button_frame.pack()
        tk.Button(button_frame, text="Books", width=15, height=2,command=self.open_books).pack(side="left", padx=5)
        tk.Button(button_frame, text="Members", width=15, height=2, command=self.open_members).pack(side="left", padx=5)
        tk.Button(button_frame, text="Issue Book", width=15, height=2, command=self.open_issue).pack(side="left", padx=5)
        tk.Button(button_frame, text="Return Book", width=15, height=2, command=self.open_return).pack(side="left", padx=5)

    def open_books(self):
        from books import BooksWindow
        BooksWindow(self.root)

    def open_members(self):
        from members import MembersWindow
        MembersWindow(self.root)

    def open_issue(self):
        from issue_book import IssueBookWindow
        IssueBookWindow(self.root)

    def open_return(self):
        from return_book import ReturnBookWindow
        ReturnBookWindow(self.root)
    def logout(self):
        answer = messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?"
        )
        if answer:
            self.root.destroy()
            root = tk.Tk()
            from login import LoginWindow
            LoginWindow(root)
            root.mainloop()

    def about(self):
        messagebox.showinfo(
            "About",
            "Library Management System\n\n"
            "Python + Tkinter + SQLite"
        )