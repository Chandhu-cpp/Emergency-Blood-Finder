# ============================================
# FILE: test_profile_window.py (Create in root)
# Test the profile window standalone
# ============================================

import tkinter as tk
from src.config.database import db

# Connect to database
db.connect()

# Create a test user
test_user = {
    'user_id': 12,
    'user_name': 'Charan Y N',
    'email': 'charanyn@donor.com',
    'role': 'donor'
}

# Create root window
root = tk.Tk()
root.title("Test Root Window")
root.geometry("300x200")

label = tk.Label(root, text="Root Window\n(Don't close this)", font=('Arial', 14))
label.pack(expand=True)

# Import and create profile setup
from src.gui.profile_completion.donor_profile_setup import DonorProfileSetup

def open_profile():
    DonorProfileSetup(root, test_user, lambda: print("Callback called!"))

button = tk.Button(root, text="Open Profile Setup", command=open_profile, 
                  font=('Arial', 12), bg='#28a745', fg='white', padx=20, pady=10)
button.pack(pady=20)

root.mainloop()

db.disconnect()