import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from database import connect_db

class IssueBookWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Issue Book")
        self.window.geometry("600x450")
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        frame = tk.Frame(self.window)
        frame.pack(pady=30)
        tk.Label(frame, text="ISSUE BOOK", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        tk.Label(frame, text="Book:").grid(row=1, column=0, padx=10, pady=10)
        self.book_combo = ttk.Combobox(frame, width=40, state="readonly")
        self.book_combo.grid(row=1, column=1)
        tk.Label(frame,text="Member:").grid(row=2, column=0, padx=10, pady=10)
        self.member_combo = ttk.Combobox(frame, width=40, state="readonly")
        self.member_combo.grid(row=2, column=1)
        tk.Label(frame, text="Issue Date:").grid(row=3, column=0, padx=10, pady=10)
        self.issue_entry = tk.Entry(frame, width=43)
        self.issue_entry.grid(row=3, column=1)
        self.issue_entry.insert(0, date.today().isoformat())
        tk.Label(frame, text="Due Date:").grid(row=4, column=0, padx=10, pady=10)
        self.due_entry = tk.Entry(frame, width=43)
        self.due_entry.grid(row=4, column=1)
        self.due_entry.insert(0, (date.today() + timedelta(days=14)).isoformat())
        tk.Button(frame, text="Issue Book", width=20, height=2, command=self.issue_book).grid(row=5, column=0, columnspan=2, pady=25)

    def load_data(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, author
            FROM books
            WHERE available > 0
            ORDER BY title
            """
        )
        books = cursor.fetchall()
        cursor.execute(
            """
            SELECT id, name
            FROM members
            ORDER BY name
            """
        )
        members = cursor.fetchall()
        conn.close()

        self.book_combo["values"] = [f"{book[0]} - {book[1]} ({book[2]})" for book in books]
        self.member_combo["values"] = [f"{member[0]} - {member[1]}" for member in members]

    def issue_book(self):
        if not self.book_combo.get():
            messagebox.showwarning(
                "Issue",
                "Select a book.",
                parent=self.window
            )
            return
        if not self.member_combo.get():
            messagebox.showwarning(
                "Issue",
                "Select a member.",
                parent=self.window
            )
            return
        book_id = int(self.book_combo.get().split(" - ")[0])
        member_id = int(self.member_combo.get().split(" - ")[0])
        issue_date = self.issue_entry.get().strip()
        due_date = self.due_entry.get().strip()
        try:
            issue = date.fromisoformat(issue_date)
            due = date.fromisoformat(due_date)
            if due < issue:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Date Error",
                "Use YYYY-MM-DD format.",
                parent=self.window
            )
            return
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT available
            FROM books
            WHERE id = ?
            """,
            (book_id,)
        )
        result = cursor.fetchone()
        if not result or result[0] <= 0:
            messagebox.showerror(
                "Issue",
                "Book is not available.",
                parent=self.window
            )
            conn.close()
            return
        cursor.execute(
            """
            INSERT INTO transactions
            (book_id, member_id, issue_date, due_date)
            VALUES (?, ?, ?, ?)
            """,
            (
                book_id,
                member_id,
                issue_date,
                due_date
            )
        )
        cursor.execute(
            """
            UPDATE books
            SET available = available - 1
            WHERE id = ?
            """,
            (book_id,)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo(
            "Success",
            "Book issued successfully.",
            parent=self.window
        )
        self.load_data()
        self.book_combo.set("")
        self.member_combo.set("")