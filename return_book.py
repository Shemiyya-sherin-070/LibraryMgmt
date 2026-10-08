import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from database import connect_db

class ReturnBookWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Return Book")
        self.window.geometry("1000x550")
        self.create_widgets()
        self.load_transactions()

    def create_widgets(self):
        tk.Label(self.window, text="RETURN BOOK", font=("Arial", 20, "bold")).pack(pady=15)
        columns = (
            "ID",
            "Book",
            "Member",
            "Issue Date",
            "Due Date",
            "Status"
        )
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")
        for column in columns:
            self.tree.heading(column, text=column)
        self.tree.column("ID", width=50)
        self.tree.column("Book", width=220)
        self.tree.column("Member", width=180)
        self.tree.column("Issue Date", width=120)
        self.tree.column("Due Date", width=120)
        self.tree.column("Status", width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Button(self.window, text="RETURN SELECTED BOOK", width=25, height=2, font=("Arial", 11, "bold"), command=self.return_book).pack(pady=10)

    def load_transactions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                t.id,
                b.title,
                m.name,
                t.issue_date,
                t.due_date,
                t.status
            FROM transactions t
            JOIN books b
            ON t.book_id = b.id
            JOIN members m
            ON t.member_id = m.id
            WHERE t.status = 'Issued'
            ORDER BY t.id DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", "end", values=row)
    def return_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning( "Return", "Select a book.", parent=self.window)
            return
        transaction_id = self.tree.item(
            selected[0]
        )["values"][0]
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT book_id, due_date
            FROM transactions
            WHERE id = ?
            AND status = 'Issued'
            """,
            (transaction_id,)
        )
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        book_id, due_date = result
        return_date = date.today()
        due = date.fromisoformat(
            due_date
        )
        late_days = max(0,(return_date - due).days)
        
        fine = late_days * 5
        cursor.execute(
            """
            UPDATE transactions
            SET return_date = ?,
                fine = ?,
                status = 'Returned'
            WHERE id = ?
            """,
            (
                return_date.isoformat(),
                fine,
                transaction_id
            )
        )
        cursor.execute(
            """
            UPDATE books
            SET available = available + 1
            WHERE id = ?
            """,
            (book_id,)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo(
            "Book Returned",
            f"Book returned successfully.\n\n"
            f"Return Date: {return_date}\n"
            f"Late Days: {late_days}\n"
            f"Fine: ₹{fine:.2f}",
            parent=self.window
        )
        self.load_transactions()