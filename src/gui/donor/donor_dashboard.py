import tkinter as tk
from tkinter import ttk, messagebox
from src.models.donor import Donor
from src.models.blood_request import BloodRequest

class DonorDashboard:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.window = tk.Toplevel()
        self.window.title(f"Donor Dashboard - {user['user_name']}")
        self.window.geometry("1000x600")
        
        self.center_window()
        self.load_donor_info()
        self.create_widgets()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_donor_info(self):
        """Load donor information"""
        donors = Donor.get_all()
        for donor in donors:
            if donor['user_id'] == self.user['user_id']:
                self.donor = donor
                break
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg='#28a745', height=60)
        header_frame.pack(fill='x')
        
        tk.Label(
            header_frame,
            text=f"🩸 Donor Dashboard - {self.user['user_name']}",
            font=('Arial', 18, 'bold'),
            bg='#28a745',
            fg='white'
        ).pack(pady=15)
        
        # Main container
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Profile Section
        profile_frame = tk.LabelFrame(main_frame, text="My Profile", font=('Arial', 12, 'bold'), padx=15, pady=15)
        profile_frame.pack(fill='x', pady=(0, 10))
        
        info_text = f"""
Name: {self.donor['name']}
Blood Group: {self.donor['blood_group']}
Email: {self.donor['email']}
Phone: {self.donor['phone']}
City Pincode: {self.donor['city_pincode']}
Total Donations: {self.donor['total_donations']}
Last Donation: {self.donor['last_donation_date'] if self.donor['last_donation_date'] else 'Never'}
Weight: {self.donor['weight']} kg
Status: {'Available ✅' if self.donor['is_available'] else 'Unavailable ❌'}
        """
        
        tk.Label(profile_frame, text=info_text, font=('Arial', 10), justify='left').pack(anchor='w')
        
        # Availability Toggle
        avail_frame = tk.Frame(profile_frame)
        avail_frame.pack(fill='x', pady=10)
        
        self.avail_var = tk.BooleanVar(value=self.donor['is_available'])
        tk.Checkbutton(
            avail_frame,
            text="I am available to donate",
            variable=self.avail_var,
            font=('Arial', 11, 'bold'),
            command=self.update_availability
        ).pack(side='left')
        
        # Donation History
        history_frame = tk.LabelFrame(main_frame, text="My Donation History", font=('Arial', 12, 'bold'), padx=10, pady=10)
        history_frame.pack(fill='both', expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(history_frame, columns=('ID', 'Date', 'Hospital', 'Units', 'Status', 'Next Eligible'), show='headings')
        
        self.tree.heading('ID', text='Donation ID')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Hospital', text='Hospital')
        self.tree.heading('Units', text='Units')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Next Eligible', text='Next Eligible Date')
        
        self.tree.column('ID', width=80)
        self.tree.column('Date', width=100)
        self.tree.column('Hospital', width=200)
        self.tree.column('Units', width=70)
        self.tree.column('Status', width=100)
        self.tree.column('Next Eligible', width=120)
        
        self.tree.pack(fill='both', expand=True)
        
        self.load_history()
        
        # Buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text="Refresh History", bg='#007bff', fg='white', 
                 command=self.load_history).pack(side='left', padx=5)
    
    def load_history(self):
        """Load donation history"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        history = Donor.get_donation_history(self.donor['donor_id'])
        
        for record in history:
            next_eligible = record['next_eligible_date'].strftime('%Y-%m-%d') if record['next_eligible_date'] else ''
            self.tree.insert('', 'end', values=(
                record['donation_id'],
                record['donation_date'].strftime('%Y-%m-%d'),
                record['hospital_name'],
                record['units_donated'],
                record['status'],
                next_eligible
            ))
    
    def update_availability(self):
        """UPDATE - Update donor availability"""
        try:
            is_available = self.avail_var.get()
            Donor.update_availability(self.donor['donor_id'], is_available)
            status = "available" if is_available else "unavailable"
            messagebox.showinfo("Success", f"Your status updated to: {status}")
            self.load_donor_info()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update availability: {str(e)}")
    
    def on_closing(self):
        self.window.destroy()
        self.parent.deiconify()

