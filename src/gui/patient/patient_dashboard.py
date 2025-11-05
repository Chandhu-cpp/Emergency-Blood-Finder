import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from src.models.blood_request import BloodRequest
from src.models.donor import Donor
from src.models.hospital import Hospital
from src.models.patient import Patient

class PatientDashboard:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.patient = None
        
        self.window = tk.Toplevel()
        self.window.title(f"Patient Dashboard - {user['user_name']}")
        self.window.geometry("1200x700")
        
        self.center_window()
        
        # Load patient info first
        if not self.load_patient_info():
            # If patient profile doesn't exist, close dashboard
            messagebox.showerror("Error", "Patient profile not found. Please contact admin.")
            self.window.destroy()
            self.parent.deiconify()
            return
        
        self.create_widgets()
        self.load_requests()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_patient_info(self):
        """Load patient information - returns False if not found"""
        try:
            patient = Patient.get_by_user_id(self.user['user_id'])
            if patient:
                self.patient = patient
                return True
            return False
        except Exception as e:
            print(f"Error loading patient info: {e}")
            return False
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg='#dc3545', height=60)
        header_frame.pack(fill='x')
        
        tk.Label(
            header_frame,
            text=f"🩸 Patient Dashboard - Welcome, {self.user['user_name']}",
            font=('Arial', 18, 'bold'),
            bg='#dc3545',
            fg='white'
        ).pack(pady=15)
        
        # Main container
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - Create Request Form
        left_frame = tk.LabelFrame(main_frame, text="Create Blood Request", font=('Arial', 12, 'bold'), padx=10, pady=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Form fields
        row = 0
        
        # Hospital Selection
        tk.Label(left_frame, text="Hospital:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=5)
        self.hospital_var = tk.StringVar()
        self.hospital_combo = ttk.Combobox(left_frame, textvariable=self.hospital_var, state='readonly', width=25)
        self.hospital_combo.grid(row=row, column=1, pady=5, sticky='w')
        self.load_hospitals()
        row += 1
        
        # Blood Group
        tk.Label(left_frame, text="Blood Group:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=5)
        self.blood_group_var = tk.StringVar(value='O+')
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        blood_group_combo = ttk.Combobox(left_frame, textvariable=self.blood_group_var, values=blood_groups, state='readonly', width=25)
        blood_group_combo.grid(row=row, column=1, pady=5, sticky='w')
        row += 1
        
        # Urgency
        tk.Label(left_frame, text="Urgency:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=5)
        self.urgency_var = tk.StringVar(value='high')
        urgency_frame = tk.Frame(left_frame)
        urgency_frame.grid(row=row, column=1, sticky='w', pady=5)
        for urgency in ['low', 'medium', 'high', 'critical']:
            tk.Radiobutton(urgency_frame, text=urgency.capitalize(), variable=self.urgency_var, value=urgency).pack(side='left')
        row += 1
        
        # Units Needed
        tk.Label(left_frame, text="Units Needed:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=5)
        self.units_var = tk.StringVar(value='1')
        units_spinbox = tk.Spinbox(left_frame, from_=1, to=10, textvariable=self.units_var, width=24)
        units_spinbox.grid(row=row, column=1, pady=5, sticky='w')
        row += 1
        
        # Required By Date
        tk.Label(left_frame, text="Required By:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=5)
        self.date_entry = DateEntry(left_frame, width=23, background='darkblue', foreground='white', borderwidth=2, 
                                    mindate=datetime.now().date(), date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=row, column=1, pady=5, sticky='w')
        row += 1
        
        # Medical Reason
        tk.Label(left_frame, text="Medical Reason:", font=('Arial', 10)).grid(row=row, column=0, sticky='nw', pady=5)
        self.reason_text = tk.Text(left_frame, width=25, height=4, wrap='word')
        self.reason_text.grid(row=row, column=1, pady=5, sticky='w')
        row += 1
        
        # Buttons
        btn_frame = tk.Frame(left_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=15)
        
        tk.Button(btn_frame, text="Create Request", bg='#28a745', fg='white', font=('Arial', 11, 'bold'), 
                 width=15, command=self.create_request).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Clear Form", bg='#6c757d', fg='white', font=('Arial', 11), 
                 width=15, command=self.clear_form).pack(side='left', padx=5)
        
        # Right side - My Requests Table
        right_frame = tk.LabelFrame(main_frame, text="My Blood Requests", font=('Arial', 12, 'bold'), padx=10, pady=10)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Treeview
        tree_frame = tk.Frame(right_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Scrollbars
        tree_scroll_y = tk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side='right', fill='y')
        tree_scroll_x = tk.Scrollbar(tree_frame, orient='horizontal')
        tree_scroll_x.pack(side='bottom', fill='x')
        
        # Table
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set,
                                 columns=('ID', 'Blood', 'Urgency', 'Status', 'Units', 'Date', 'Donor'), show='headings')
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Columns
        self.tree.heading('ID', text='Req ID')
        self.tree.heading('Blood', text='Blood Group')
        self.tree.heading('Urgency', text='Urgency')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Units', text='Units')
        self.tree.heading('Date', text='Request Date')
        self.tree.heading('Donor', text='Matched Donor')
        
        self.tree.column('ID', width=60)
        self.tree.column('Blood', width=80)
        self.tree.column('Urgency', width=80)
        self.tree.column('Status', width=80)
        self.tree.column('Units', width=60)
        self.tree.column('Date', width=120)
        self.tree.column('Donor', width=120)
        
        self.tree.pack(fill='both', expand=True)
        
        # Action buttons
        action_frame = tk.Frame(right_frame)
        action_frame.pack(fill='x', pady=10)
        
        tk.Button(action_frame, text="Refresh", bg='#007bff', fg='white', command=self.load_requests).pack(side='left', padx=5)
        tk.Button(action_frame, text="View Details", bg='#17a2b8', fg='white', command=self.view_details).pack(side='left', padx=5)
        tk.Button(action_frame, text="Cancel Request", bg='#dc3545', fg='white', command=self.cancel_request).pack(side='left', padx=5)
        tk.Button(action_frame, text="Search Donors", bg='#ffc107', command=self.search_donors).pack(side='left', padx=5)
    
    def load_hospitals(self):
        """Load hospitals into combobox"""
        try:
            hospitals = Hospital.get_all()
            hospital_list = [f"{h['hospital_id']} - {h['hospital_name']}" for h in hospitals]
            self.hospital_combo['values'] = hospital_list
            if hospital_list:
                self.hospital_combo.current(0)
        except Exception as e:
            print(f"Error loading hospitals: {e}")
    
    def load_requests(self):
        """Load all blood requests for this patient"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Fetch requests
            requests = BloodRequest.get_all()
            
            # Filter by current user
            user_requests = [r for r in requests if r.get('patient_name') == self.user['user_name']]
            
            for req in user_requests:
                donor_name = req.get('donor_name', 'Not Matched')
                request_date = req.get('request_date')
                date_str = request_date.strftime('%Y-%m-%d %H:%M') if request_date else 'N/A'
                
                self.tree.insert('', 'end', values=(
                    req['request_id'],
                    req['blood_group_needed'],
                    req['urgency'],
                    req['status'],
                    req['units_needed'],
                    date_str,
                    donor_name
                ))
        except Exception as e:
            print(f"Error loading requests: {e}")
            messagebox.showerror("Error", f"Failed to load requests: {str(e)}")
    
    def create_request(self):
        """CREATE - Create new blood request"""
        try:
            # Get hospital ID from selection
            hospital_text = self.hospital_var.get()
            if not hospital_text:
                messagebox.showerror("Error", "Please select a hospital")
                return
            
            hospital_id = int(hospital_text.split(' - ')[0])
            blood_group = self.blood_group_var.get()
            urgency = self.urgency_var.get()
            units = int(self.units_var.get())
            required_date = self.date_entry.get_date()
            reason = self.reason_text.get('1.0', 'end-1c').strip()
            
            if not reason:
                messagebox.showerror("Error", "Please provide medical reason")
                return
            
            # Create request (trigger will auto-match donor)
            result = BloodRequest.create(
                self.user['user_id'],
                hospital_id,
                blood_group,
                urgency,
                units,
                reason,
                required_date
            )
            
            match_info = ""
            if result['match']:
                match_info = f"\n\n✅ Donor Matched: {result['match']['name']}\nPhone: {result['match']['phone']}"
            else:
                match_info = "\n\n⚠️ No donor matched yet. We'll notify you when a donor is available."
            
            messagebox.showinfo("Success", f"Blood request created successfully!{match_info}")
            self.clear_form()
            self.load_requests()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create request: {str(e)}")
    
    def view_details(self):
        """READ - View request details"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a request to view")
            return
        
        item = self.tree.item(selected[0])
        request_id = item['values'][0]
        
        # Fetch full details
        request = BloodRequest.get_by_id(request_id)
        match = BloodRequest.get_match(request_id)
        
        details = f"""
Request ID: {request['request_id']}
Blood Group: {request['blood_group_needed']}
Urgency: {request['urgency']}
Status: {request['status']}
Units Needed: {request['units_needed']}
Medical Reason: {request['medical_reason']}
Hospital: {request.get('hospital_name', 'N/A')}
Request Date: {request.get('request_date', 'N/A')}
Required By: {request.get('required_by_date', 'N/A')}
        """
        
        if match:
            details += f"""
\n--- Matched Donor ---
Name: {match['name']}
Phone: {match.get('phone', 'N/A')}
Blood Group: {match['blood_group']}
Match Status: {match['match_status']}
            """
        
        # Create details window
        details_window = tk.Toplevel(self.window)
        details_window.title("Request Details")
        details_window.geometry("400x500")
        
        text = tk.Text(details_window, wrap='word', font=('Arial', 10), padx=10, pady=10)
        text.pack(fill='both', expand=True)
        text.insert('1.0', details)
        text.config(state='disabled')
    
    def cancel_request(self):
        """UPDATE/DELETE - Cancel blood request"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a request to cancel")
            return
        
        item = self.tree.item(selected[0])
        request_id = item['values'][0]
        status = item['values'][3]
        
        if status == 'fulfilled':
            messagebox.showinfo("Info", "Cannot cancel a fulfilled request")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this request?"):
            try:
                BloodRequest.update_status(request_id, 'cancelled')
                messagebox.showinfo("Success", "Request cancelled successfully")
                self.load_requests()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel request: {str(e)}")
    
    def search_donors(self):
        """READ - Search available donors"""
        blood_group = self.blood_group_var.get()
        donors = Donor.get_available(blood_group)
        
        # Create search window
        search_window = tk.Toplevel(self.window)
        search_window.title(f"Available Donors - {blood_group}")
        search_window.geometry("700x400")
        
        tk.Label(search_window, text=f"Available Donors for {blood_group}", 
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Treeview
        tree = ttk.Treeview(search_window, columns=('ID', 'Name', 'Blood', 'Phone', 'City', 'Last Donation'), show='headings')
        
        tree.heading('ID', text='Donor ID')
        tree.heading('Name', text='Name')
        tree.heading('Blood', text='Blood Group')
        tree.heading('Phone', text='Phone')
        tree.heading('City', text='Pincode')
        tree.heading('Last Donation', text='Last Donation')
        
        tree.column('ID', width=70)
        tree.column('Name', width=150)
        tree.column('Blood', width=90)
        tree.column('Phone', width=120)
        tree.column('City', width=80)
        tree.column('Last Donation', width=120)
        
        for donor in donors:
            last_donation = donor.get('last_donation_date')
            last_donation_str = last_donation.strftime('%Y-%m-%d') if last_donation else 'Never'
            
            tree.insert('', 'end', values=(
                donor['donor_id'],
                donor['name'],
                donor['blood_group'],
                donor.get('phone', 'N/A'),
                donor['city_pincode'],
                last_donation_str
            ))
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(search_window, text=f"Total Available Donors: {len(donors)}", 
                font=('Arial', 11)).pack(pady=5)
    
    def clear_form(self):
        """Clear form fields"""
        self.blood_group_var.set('O+')
        self.urgency_var.set('high')
        self.units_var.set('1')
        self.date_entry.set_date(datetime.now().date())
        self.reason_text.delete('1.0', 'end')
    
    def on_closing(self):
        """Handle window close"""
        self.window.destroy()
        self.parent.deiconify()