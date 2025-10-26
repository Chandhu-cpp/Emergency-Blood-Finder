import tkinter as tk
from tkinter import ttk, messagebox
from src.models.user import User
from src.gui.patient.patient_dashboard import PatientDashboard
from src.gui.donor.donor_dashboard import DonorDashboard
from src.gui.admin.admin_dashboard import AdminDashboard

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Emergency Blood Finder - Login")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        self.create_widgets()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#dc3545', height=80)
        title_frame.pack(fill='x')
        
        title_label = tk.Label(
            title_frame, 
            text="🩸 Emergency Blood Finder", 
            font=('Arial', 24, 'bold'),
            bg='#dc3545',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Login Form
        form_frame = tk.Frame(self.root, padx=50, pady=30)
        form_frame.pack(fill='both', expand=True)
        
        # Email
        tk.Label(form_frame, text="Email:", font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=10)
        self.email_entry = tk.Entry(form_frame, font=('Arial', 12), width=30)
        self.email_entry.grid(row=0, column=1, pady=10)
        
        # Role Selection
        tk.Label(form_frame, text="Login As:", font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=10)
        self.role_var = tk.StringVar(value='patient')
        roles = [('Patient', 'patient'), ('Donor', 'donor'), ('Admin', 'admin'), ('Hospital Staff', 'hospital_staff')]
        
        role_frame = tk.Frame(form_frame)
        role_frame.grid(row=1, column=1, pady=10, sticky='w')
        
        for text, value in roles:
            tk.Radiobutton(
                role_frame, 
                text=text, 
                variable=self.role_var, 
                value=value,
                font=('Arial', 10)
            ).pack(anchor='w')
        
        # Login Button
        login_btn = tk.Button(
            form_frame,
            text="Login",
            font=('Arial', 14, 'bold'),
            bg='#28a745',
            fg='white',
            width=20,
            height=2,
            command=self.login
        )
        login_btn.grid(row=2, column=0, columnspan=2, pady=30)
    
    def login(self):
        email = self.email_entry.get().strip()
        role = self.role_var.get()
        
        if not email:
            messagebox.showerror("Error", "Please enter your email")
            return
        
        # Authenticate user
        user = User.authenticate(email, role)
        
        if user:
            messagebox.showinfo("Success", f"Welcome, {user['user_name']}!")
            self.root.withdraw()  # Hide login window
            
            # Open appropriate dashboard
            if role == 'patient':
                PatientDashboard(self.root, user)
            elif role == 'donor':
                DonorDashboard(self.root, user)
            elif role == 'admin':
                AdminDashboard(self.root, user)
            elif role == 'hospital_staff':
                # HospitalDashboard(self.root, user)
                messagebox.showinfo("Info", "Hospital dashboard coming soon!")
        else:
            messagebox.showerror("Error", "Invalid credentials or user not found")