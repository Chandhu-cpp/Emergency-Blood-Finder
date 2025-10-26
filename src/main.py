import tkinter as tk
from src.config.database import db
from src.gui.login_window import LoginWindow

def main():
    # Connect to database
    if not db.connect():
        print("Failed to connect to database. Exiting...")
        return
    
    # Create main window
    root = tk.Tk()
    app = LoginWindow(root)
    
    # Run application
    root.mainloop()
    
    # Disconnect database when closing
    db.disconnect()

if __name__ == "__main__":
    main()