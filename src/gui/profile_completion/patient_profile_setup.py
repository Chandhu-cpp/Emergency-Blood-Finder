import tkinter as tk
from tkinter import ttk, messagebox
from src.models.patient import Patient

class PatientProfileSetup:
    def __init__(self, parent, user, callback):
        print(f"DEBUG: Initializing PatientProfileSetup for {user['user_name']}")
        
        self.parent = parent
        self.user = user
        self.callback = callback
        
        try:
            self.window = tk.Toplevel(parent)
            self.window.title("Complete Your Patient Profile")
            self.window.geometry("500x650")  # Increased height from 550 to 650
            self.window.resizable(False, False)
            
            # CRITICAL: Make window visible BEFORE making it modal
            self.window.deiconify()
            self.window.update()
            
            self.center_window()
            self.create_widgets()
            
            # Make it modal AFTER creating widgets
            self.window.transient(parent)
            self.window.grab_set()
            
            # Bring to front - multiple attempts
            self.window.lift()
            self.window.attributes('-topmost', True)
            self.window.after(100, lambda: self.window.attributes('-topmost', False))
            self.window.focus_force()
            
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            print("DEBUG: PatientProfileSetup window created successfully")
            print(f"DEBUG: Window state: {self.window.state()}")
            print(f"DEBUG: Window visible: {self.window.winfo_viewable()}")
            
        except Exception as e:
            print(f"ERROR creating PatientProfileSetup: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to open profile setup: {str(e)}")
            parent.deiconify()
    
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self.window, bg='#dc3545', height=80)
        header.pack(fill='x')
        
        tk.Label(
            header,
            text="🩸 Complete Your Patient Profile",
            font=('Arial', 18, 'bold'),
            bg='#dc3545',
            fg='white'
        ).pack(pady=25)
        
        # Info message
        info_frame = tk.Frame(self.window, bg='#fff3cd', padx=10, pady=10)
        info_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(
            info_frame,
            text="⚠️ Please complete your profile to continue",
            font=('Arial', 11),
            bg='#fff3cd',
            fg='#856404'
        ).pack()
        
        # Form
        form_frame = tk.Frame(self.window, padx=40, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        row = 0
        
        # Name (pre-filled)
        tk.Label(form_frame, text="Full Name:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=8)
        self.name_var = tk.StringVar(value=self.user['user_name'])
        tk.Entry(form_frame, textvariable=self.name_var, width=30, font=('Arial', 10)).grid(row=row, column=1, pady=8)
        row += 1
        
        # Blood Group
        tk.Label(form_frame, text="Blood Group:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=8)
        self.blood_group_var = tk.StringVar(value='O+')
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        ttk.Combobox(form_frame, textvariable=self.blood_group_var, values=blood_groups, 
                     state='readonly', width=28, font=('Arial', 10)).grid(row=row, column=1, pady=8)
        row += 1
        
        # City Pincode
        tk.Label(form_frame, text="City Pincode:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=8)
        self.pincode_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.pincode_var, width=30, font=('Arial', 10)).grid(row=row, column=1, pady=8)
        tk.Label(form_frame, text="(6 digits)", font=('Arial', 8), fg='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Emergency Contact
        tk.Label(form_frame, text="Emergency Contact:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=8)
        self.emergency_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.emergency_var, width=30, font=('Arial', 10)).grid(row=row, column=1, pady=8)
        tk.Label(form_frame, text="(10 digits)", font=('Arial', 8), fg='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Medical History (Optional)
        tk.Label(form_frame, text="Medical History:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='nw', pady=8)
        self.medical_text = tk.Text(form_frame, width=30, height=5, wrap='word', font=('Arial', 10))
        self.medical_text.grid(row=row, column=1, pady=8)
        tk.Label(form_frame, text="(Optional)", font=('Arial', 8), fg='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Buttons
        btn_frame = tk.Frame(self.window, pady=20)
        btn_frame.pack()
        
        tk.Button(
            btn_frame,
            text="Complete Profile",
            font=('Arial', 12, 'bold'),
            bg='#dc3545',
            fg='white',
            width=18,
            height=2,
            command=self.save_profile
        ).pack(side='left', padx=10)
        
        tk.Button(
            btn_frame,
            text="Logout",
            font=('Arial', 12),
            bg='#6c757d',
            fg='white',
            width=10,
            height=2,
            command=self.logout
        ).pack(side='left', padx=10)
    
    def save_profile(self):
        """Save patient profile"""
        print("DEBUG: Saving patient profile...")
        
        name = self.name_var.get().strip()
        blood_group = self.blood_group_var.get()
        pincode = self.pincode_var.get().strip()
        emergency = self.emergency_var.get().strip()
        medical_history = self.medical_text.get('1.0', 'end-1c').strip()
        
        # Validation
        if not all([name, blood_group, pincode, emergency]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        if len(pincode) != 6 or not pincode.isdigit():
            messagebox.showerror("Error", "Please enter a valid 6-digit pincode")
            return
        
        if len(emergency) != 10 or not emergency.isdigit():
            messagebox.showerror("Error", "Please enter a valid 10-digit emergency contact number")
            return
        
        try:
            print(f"DEBUG: Creating patient profile for user_id: {self.user['user_id']}")
            
            # Create patient profile
            Patient.create(
                self.user['user_id'],
                name,
                blood_group,
                pincode,
                emergency,
                medical_history if medical_history else 'No major medical history'
            )
            
            print("DEBUG: Patient profile created successfully")
            messagebox.showinfo("Success", "Profile completed successfully!")
            
            self.window.destroy()
            
            # Call callback to open dashboard
            if self.callback:
                print("DEBUG: Calling callback to open dashboard")
                self.callback()
            
        except Exception as e:
            print(f"ERROR saving patient profile: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")
    
    def logout(self):
        """Logout without completing profile"""
        if messagebox.askyesno("Confirm", "Are you sure you want to logout without completing your profile?"):
            print("DEBUG: User chose to logout without completing profile")
            self.window.destroy()
            self.parent.deiconify()
    
    def on_closing(self):
        """Prevent closing without action"""
        self.logout()