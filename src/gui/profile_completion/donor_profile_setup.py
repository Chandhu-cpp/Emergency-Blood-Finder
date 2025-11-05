import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.models.donor import Donor

# Try to import tkcalendar, if not available use basic Entry
try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    print("Warning: tkcalendar not installed. Using basic date entry.")

class DonorProfileSetup:
    def __init__(self, parent, user, callback):
        print(f"DEBUG: Initializing DonorProfileSetup for {user['user_name']}")
        
        self.parent = parent
        self.user = user
        self.callback = callback
        
        try:
            self.window = tk.Toplevel(parent)
            self.window.title("Complete Your Donor Profile")
            self.window.geometry("500x700")  # Increased height from 600 to 700
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
            
            # Prevent closing without completing
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            print("DEBUG: DonorProfileSetup window created successfully")
            print(f"DEBUG: Window state: {self.window.state()}")
            print(f"DEBUG: Window visible: {self.window.winfo_viewable()}")
            
        except Exception as e:
            print(f"ERROR creating DonorProfileSetup: {e}")
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
        header = tk.Frame(self.window, bg='#28a745', height=80)
        header.pack(fill='x')
        
        tk.Label(
            header,
            text="🩸 Complete Your Donor Profile",
            font=('Arial', 18, 'bold'),
            bg='#28a745',
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
        
        # Name (pre-filled from USER table)
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
        
        # Weight
        tk.Label(form_frame, text="Weight (kg):", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=8)
        self.weight_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.weight_var, width=30, font=('Arial', 10)).grid(row=row, column=1, pady=8)
        tk.Label(form_frame, text="(Minimum: 45 kg)", font=('Arial', 8), fg='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Last Donation Date (Optional)
        tk.Label(form_frame, text="Last Donation:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky='w', pady=8)
        
        date_frame = tk.Frame(form_frame)
        date_frame.grid(row=row, column=1, sticky='w', pady=8)
        
        self.has_donated_var = tk.BooleanVar(value=False)
        tk.Radiobutton(date_frame, text="Never donated", variable=self.has_donated_var, 
                      value=False, command=self.toggle_date).pack(anchor='w')
        tk.Radiobutton(date_frame, text="Select date", variable=self.has_donated_var, 
                      value=True, command=self.toggle_date).pack(anchor='w')
        
        row += 1
        
        # Date entry widget
        if CALENDAR_AVAILABLE:
            self.date_entry = DateEntry(form_frame, width=28, background='darkblue', 
                                        foreground='white', borderwidth=2, 
                                        date_pattern='yyyy-mm-dd', state='disabled')
        else:
            # Fallback to regular Entry
            self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
            self.date_entry = tk.Entry(form_frame, textvariable=self.date_var, width=30, 
                                       font=('Arial', 10), state='disabled')
        
        self.date_entry.grid(row=row, column=1, pady=8)
        tk.Label(form_frame, text="(Format: YYYY-MM-DD)", font=('Arial', 8), fg='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Buttons
        btn_frame = tk.Frame(self.window, pady=20)
        btn_frame.pack()
        
        tk.Button(
            btn_frame,
            text="Complete Profile",
            font=('Arial', 12, 'bold'),
            bg='#28a745',
            fg='white',
            width=18,
            height=2,
            command=self.save_profile
        ).pack(side='left', padx=10)
        
        tk.Button(
            btn_frame,
            text="Logout",
            font=('Arial', 12),
            bg='#dc3545',
            fg='white',
            width=10,
            height=2,
            command=self.logout
        ).pack(side='left', padx=10)
    
    def toggle_date(self):
        """Enable/disable date picker based on selection"""
        if self.has_donated_var.get():
            self.date_entry.config(state='normal')
        else:
            self.date_entry.config(state='disabled')
    
    def save_profile(self):
        """Save donor profile"""
        print("DEBUG: Saving donor profile...")
        
        name = self.name_var.get().strip()
        blood_group = self.blood_group_var.get()
        pincode = self.pincode_var.get().strip()
        weight_str = self.weight_var.get().strip()
        
        # Validation
        if not all([name, blood_group, pincode, weight_str]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        try:
            weight = float(weight_str)
            if weight < 45:
                messagebox.showerror("Error", "Weight must be at least 45 kg to donate blood")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid weight")
            return
        
        if len(pincode) != 6 or not pincode.isdigit():
            messagebox.showerror("Error", "Please enter a valid 6-digit pincode")
            return
        
        # Get last donation date
        last_donation = None
        if self.has_donated_var.get():
            try:
                if CALENDAR_AVAILABLE:
                    last_donation = self.date_entry.get_date()
                else:
                    date_str = self.date_var.get()
                    last_donation = datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
                return
        
        try:
            print(f"DEBUG: Creating donor profile for user_id: {self.user['user_id']}")
            
            # Create donor profile
            Donor.create(
                self.user['user_id'],
                name,
                blood_group,
                pincode,
                weight,
                last_donation
            )
            
            print("DEBUG: Donor profile created successfully")
            messagebox.showinfo("Success", "Profile completed successfully!")
            
            self.window.destroy()
            
            # Call callback to open dashboard
            if self.callback:
                print("DEBUG: Calling callback to open dashboard")
                self.callback()
            
        except Exception as e:
            print(f"ERROR saving donor profile: {e}")
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

