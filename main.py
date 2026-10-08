import tkinter as tk

from database import initialize_database
from login import LoginWindow

def main():
    initialize_database()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()