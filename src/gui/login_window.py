import tkinter as tk
from tkinter import ttk, messagebox
from src.models.user import User
from src.models.donor import Donor
from src.models.patient import Patient
from src.gui.patient.patient_dashboard import PatientDashboard
from src.gui.donor.donor_dashboard import DonorDashboard
from src.gui.admin.admin_dashboard import AdminDashboard

# Import profile setup windows
try:
    from src.gui.profile_completion.donor_profile_setup import DonorProfileSetup
    from src.gui.profile_completion.patient_profile_setup import PatientProfileSetup
    PROFILE_SETUP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Profile setup modules not found: {e}")
    PROFILE_SETUP_AVAILABLE = False

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Emergency Blood Finder - Login")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
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
        
        try:
            # Authenticate user
            user = User.authenticate(email, role)
            
            if user:
                print(f"DEBUG: User authenticated: {user['user_name']}, Role: {role}")
                self.root.withdraw()  # Hide login window
                
                # Check role and profile completion
                if role == 'patient':
                    self.handle_patient_login(user)
                elif role == 'donor':
                    self.handle_donor_login(user)
                elif role == 'admin':
                    self.handle_admin_login(user)
                elif role == 'hospital_staff':
                    self.handle_hospital_login(user)
            else:
                messagebox.showerror("Error", "Invalid credentials or user not found")
        
        except Exception as e:
            print(f"ERROR in login: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Login failed: {str(e)}")
            self.root.deiconify()
    
    def handle_patient_login(self, user):
        """Handle patient login with profile check"""
        try:
            print(f"DEBUG: Checking patient profile for user_id: {user['user_id']}")
            
            # Check if patient profile exists
            patient_profile = Patient.get_by_user_id(user['user_id'])
            
            if patient_profile:
                print("DEBUG: Patient profile found, opening dashboard")
                # Profile exists, open dashboard directly
                PatientDashboard(self.root, user)
            else:
                print("DEBUG: Patient profile not found, showing setup")
                # DON'T hide login window yet - profile setup needs visible parent
                self.root.deiconify()  # Make sure parent is visible
                
                if PROFILE_SETUP_AVAILABLE:
                    def open_dashboard():
                        print("DEBUG: Profile completed, opening dashboard")
                        self.root.withdraw()  # NOW hide login window
                        PatientDashboard(self.root, user)
                    
                    PatientProfileSetup(self.root, user, open_dashboard)
                else:
                    messagebox.showerror("Error", "Profile setup module not available. Please contact admin.")
                    self.root.deiconify()
        
        except Exception as e:
            print(f"ERROR in handle_patient_login: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load patient dashboard: {str(e)}")
            self.root.deiconify()
    
    def handle_donor_login(self, user):
        """Handle donor login with profile check"""
        try:
            print(f"DEBUG: Checking donor profile for user_id: {user['user_id']}")
            
            # Check if donor profile exists
            donor_profile = Donor.get_by_user_id(user['user_id'])
            
            if donor_profile:
                print("DEBUG: Donor profile found, opening dashboard")
                # Profile exists, open dashboard directly
                DonorDashboard(self.root, user)
            else:
                print("DEBUG: Donor profile not found, showing setup")
                # DON'T hide login window yet - profile setup needs visible parent
                self.root.deiconify()  # Make sure parent is visible
                
                if PROFILE_SETUP_AVAILABLE:
                    def open_dashboard():
                        print("DEBUG: Profile completed, opening dashboard")
                        self.root.withdraw()  # NOW hide login window
                        DonorDashboard(self.root, user)
                    
                    DonorProfileSetup(self.root, user, open_dashboard)
                else:
                    messagebox.showerror("Error", "Profile setup module not available. Please contact admin.")
                    self.root.deiconify()
        
        except Exception as e:
            print(f"ERROR in handle_donor_login: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load donor dashboard: {str(e)}")
            self.root.deiconify()
    
    def handle_admin_login(self, user):
        """Handle admin login"""
        try:
            print("DEBUG: Opening admin dashboard")
            AdminDashboard(self.root, user)
        except Exception as e:
            print(f"ERROR in handle_admin_login: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load admin dashboard: {str(e)}")
            self.root.deiconify()

    def handle_hospital_login(self, user):
        """Handle hospital staff login"""
        try:
            print("DEBUG: Opening hospital dashboard")
            from src.gui.hospital.hospital_dashboard import HospitalDashboard
            HospitalDashboard(self.root, user)
        except Exception as e:
            print(f"ERROR in handle_hospital_login: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load hospital dashboard: {str(e)}")
            self.root.deiconify()
