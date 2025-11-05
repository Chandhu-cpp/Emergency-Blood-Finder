import tkinter as tk
from tkinter import ttk, messagebox
from src.models.donor import Donor
from src.models.blood_request import BloodRequest
from src.models.donor_match import DonorMatch

class DonorDashboard:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.donor = None
        
        self.window = tk.Toplevel()
        self.window.title(f"Donor Dashboard - {user['user_name']}")
        self.window.geometry("1200x700")
        
        self.center_window()
        
        # Load donor info first
        if not self.load_donor_info():
            messagebox.showerror("Error", "Donor profile not found. Please contact admin.")
            self.window.destroy()
            self.parent.deiconify()
            return
        
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
        """Load donor information - returns False if not found"""
        try:
            donor = Donor.get_by_user_id(self.user['user_id'])
            if donor:
                self.donor = donor
                return True
            return False
        except Exception as e:
            print(f"Error loading donor info: {e}")
            return False
    
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
        
        # Main container with two columns
        main_frame = tk.Frame(self.window, padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        # Left column - Profile and Pending Matches
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Profile Section
        profile_frame = tk.LabelFrame(left_frame, text="My Profile", font=('Arial', 12, 'bold'), padx=15, pady=15)
        profile_frame.pack(fill='x', pady=(0, 10))
        
        last_donation = self.donor.get('last_donation_date')
        last_donation_str = last_donation.strftime('%Y-%m-%d') if last_donation else 'Never'
        
        info_text = f"""
Name: {self.donor.get('name', 'N/A')}
Blood Group: {self.donor.get('blood_group', 'N/A')}
Email: {self.donor.get('email', 'N/A')}
Phone: {self.donor.get('phone', 'N/A')}
City Pincode: {self.donor.get('city_pincode', 'N/A')}
Total Donations: {self.donor.get('total_donations', 0)}
Last Donation: {last_donation_str}
Weight: {self.donor.get('weight', 'N/A')} kg
Status: {'Available ✅' if self.donor.get('is_available', False) else 'Unavailable ❌'}
        """
        
        tk.Label(profile_frame, text=info_text, font=('Arial', 10), justify='left').pack(anchor='w')
        
        # Availability Toggle
        avail_frame = tk.Frame(profile_frame)
        avail_frame.pack(fill='x', pady=10)
        
        self.avail_var = tk.BooleanVar(value=self.donor.get('is_available', False))
        tk.Checkbutton(
            avail_frame,
            text="I am available to donate",
            variable=self.avail_var,
            font=('Arial', 11, 'bold'),
            command=self.update_availability
        ).pack(side='left')
        
        # PENDING MATCHES SECTION (NEW!)
        matches_frame = tk.LabelFrame(left_frame, text="🔔 Pending Blood Requests Matched to You", 
                                       font=('Arial', 12, 'bold'), padx=10, pady=10, bg='#fff3cd')
        matches_frame.pack(fill='both', expand=True)
        
        # Matches Treeview
        matches_tree_frame = tk.Frame(matches_frame)
        matches_tree_frame.pack(fill='both', expand=True)
        
        matches_scroll = tk.Scrollbar(matches_tree_frame)
        matches_scroll.pack(side='right', fill='y')
        
        self.matches_tree = ttk.Treeview(matches_tree_frame, yscrollcommand=matches_scroll.set,
                                         columns=('Match ID', 'Patient', 'Blood', 'Urgency', 'Units', 'Hospital', 'Date', 'Status'),
                                         show='headings', height=8)
        
        matches_scroll.config(command=self.matches_tree.yview)
        
        self.matches_tree.heading('Match ID', text='Match ID')
        self.matches_tree.heading('Patient', text='Patient Name')
        self.matches_tree.heading('Blood', text='Blood Group')
        self.matches_tree.heading('Urgency', text='Urgency')
        self.matches_tree.heading('Units', text='Units')
        self.matches_tree.heading('Hospital', text='Hospital')
        self.matches_tree.heading('Date', text='Request Date')
        self.matches_tree.heading('Status', text='Match Status')
        
        self.matches_tree.column('Match ID', width=70)
        self.matches_tree.column('Patient', width=120)
        self.matches_tree.column('Blood', width=80)
        self.matches_tree.column('Urgency', width=70)
        self.matches_tree.column('Units', width=50)
        self.matches_tree.column('Hospital', width=150)
        self.matches_tree.column('Date', width=100)
        self.matches_tree.column('Status', width=80)
        
        self.matches_tree.pack(fill='both', expand=True)
        
        # Action buttons for matches
        match_btn_frame = tk.Frame(matches_frame, bg='#fff3cd')
        match_btn_frame.pack(fill='x', pady=10)
        
        tk.Button(match_btn_frame, text="Refresh", bg='#007bff', fg='white', 
                 command=self.load_matches).pack(side='left', padx=5)
        tk.Button(match_btn_frame, text="Accept Request", bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                 command=self.accept_request).pack(side='left', padx=5)
        tk.Button(match_btn_frame, text="Decline Request", bg='#dc3545', fg='white',
                 command=self.decline_request).pack(side='left', padx=5)
        tk.Button(match_btn_frame, text="View Details", bg='#17a2b8', fg='white',
                 command=self.view_match_details).pack(side='left', padx=5)
        
        # Right column - Donation History
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        history_frame = tk.LabelFrame(right_frame, text="My Donation History", font=('Arial', 12, 'bold'), padx=10, pady=10)
        history_frame.pack(fill='both', expand=True)
        
        # History Treeview
        history_tree_frame = tk.Frame(history_frame)
        history_tree_frame.pack(fill='both', expand=True)
        
        history_scroll = tk.Scrollbar(history_tree_frame)
        history_scroll.pack(side='right', fill='y')
        
        self.history_tree = ttk.Treeview(history_tree_frame, yscrollcommand=history_scroll.set,
                                        columns=('ID', 'Date', 'Hospital', 'Units', 'Status', 'Next Eligible'), 
                                        show='headings')
        
        history_scroll.config(command=self.history_tree.yview)
        
        self.history_tree.heading('ID', text='Donation ID')
        self.history_tree.heading('Date', text='Date')
        self.history_tree.heading('Hospital', text='Hospital')
        self.history_tree.heading('Units', text='Units')
        self.history_tree.heading('Status', text='Status')
        self.history_tree.heading('Next Eligible', text='Next Eligible Date')
        
        self.history_tree.column('ID', width=80)
        self.history_tree.column('Date', width=100)
        self.history_tree.column('Hospital', width=200)
        self.history_tree.column('Units', width=70)
        self.history_tree.column('Status', width=100)
        self.history_tree.column('Next Eligible', width=120)
        
        self.history_tree.pack(fill='both', expand=True)
        
        # Refresh button for history
        tk.Button(history_frame, text="Refresh History", bg='#007bff', fg='white', 
                 command=self.load_history).pack(pady=10)
        
        # Load initial data
        self.load_matches()
        self.load_history()
    
    def load_matches(self):
        """Load pending blood requests matched to this donor"""
        # Clear existing items
        for item in self.matches_tree.get_children():
            self.matches_tree.delete(item)
        
        try:
            # Get matches for this donor
            matches = DonorMatch.get_by_donor_id(self.donor['donor_id'])
            
            for match in matches:
                # Only show matched or contacted status (not confirmed/rejected)
                if match.get('match_status') in ['matched', 'contacted']:
                    request_date = match.get('request_date')
                    date_str = request_date.strftime('%Y-%m-%d') if request_date else 'N/A'
                    
                    self.matches_tree.insert('', 'end', values=(
                        match.get('match_id', 'N/A'),
                        match.get('patient_name', 'N/A'),
                        match.get('blood_group_needed', 'N/A'),
                        match.get('urgency', 'N/A'),
                        match.get('units_needed', 'N/A'),
                        match.get('hospital_name', 'N/A'),
                        date_str,
                        match.get('match_status', 'N/A')
                    ))
            
            # Update count in label
            count = len(self.matches_tree.get_children())
            if count > 0:
                messagebox.showinfo("New Matches!", f"You have {count} pending blood request(s) matched to you!")
                
        except Exception as e:
            print(f"Error loading matches: {e}")
            messagebox.showerror("Error", f"Failed to load matches: {str(e)}")
    
    def accept_request(self):
        """Accept a blood request match"""
        selected = self.matches_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a request to accept")
            return
        
        item = self.matches_tree.item(selected[0])
        match_id = item['values'][0]
        patient_name = item['values'][1]
        urgency = item['values'][3]
        
        if messagebox.askyesno("Confirm Donation", 
                              f"Accept blood donation request from {patient_name}?\n\n"
                              f"Urgency: {urgency}\n"
                              f"You will be contacted by the hospital to schedule the donation."):
            try:
                # Update match status to confirmed
                DonorMatch.update_status(match_id, 'confirmed', 
                                        f"Donor {self.donor['name']} confirmed availability")
                
                messagebox.showinfo("Success", 
                                   "Request accepted! ✅\n\n"
                                   "The hospital will contact you soon to schedule your donation.\n"
                                   "Thank you for saving a life!")
                
                self.load_matches()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to accept request: {str(e)}")
    
    def decline_request(self):
        """Decline a blood request match"""
        selected = self.matches_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a request to decline")
            return
        
        item = self.matches_tree.item(selected[0])
        match_id = item['values'][0]
        patient_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Decline", 
                              f"Decline blood donation request from {patient_name}?\n\n"
                              f"Another donor will be matched instead."):
            try:
                # Update match status to rejected
                DonorMatch.update_status(match_id, 'rejected', 
                                        f"Donor {self.donor['name']} declined")
                
                # Make donor available again
                Donor.update_availability(self.donor['donor_id'], True)
                
                messagebox.showinfo("Request Declined", 
                                   "Request declined. The system will find another donor.")
                
                self.load_matches()
                self.load_donor_info()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to decline request: {str(e)}")
    
    def view_match_details(self):
        """View detailed information about a match"""
        selected = self.matches_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a request to view")
            return
        
        item = self.matches_tree.item(selected[0])
        match_id = item['values'][0]
        
        try:
            # Get full match details
            match = DonorMatch.get_by_id(match_id)
            
            if match:
                details = f"""
═══════════════════════════════════
        BLOOD REQUEST DETAILS
═══════════════════════════════════

Match ID: {match.get('match_id', 'N/A')}
Match Date: {match.get('match_date', 'N/A')}
Match Status: {match.get('match_status', 'N/A').upper()}

--- Patient Information ---
Patient Name: {match.get('patient_name', 'N/A')}
Blood Group Needed: {match.get('blood_group_needed', 'N/A')}
Units Needed: {match.get('units_needed', 'N/A')}

--- Request Details ---
Urgency: {match.get('urgency', 'N/A').upper()}
Medical Reason: {match.get('medical_reason', 'N/A')}
Request Date: {match.get('request_date', 'N/A')}
Required By: {match.get('required_by_date', 'N/A')}

--- Hospital Information ---
Hospital: {match.get('hospital_name', 'N/A')}
Hospital Phone: {match.get('hospital_phone', 'N/A')}
City: {match.get('city', 'N/A')}

═══════════════════════════════════
                """
                
                # Create details window
                details_window = tk.Toplevel(self.window)
                details_window.title("Blood Request Details")
                details_window.geometry("500x650")
                details_window.resizable(False, False)
                
                # Center window
                details_window.update_idletasks()
                width = details_window.winfo_width()
                height = details_window.winfo_height()
                x = (details_window.winfo_screenwidth() // 2) - (width // 2)
                y = (details_window.winfo_screenheight() // 2) - (height // 2)
                details_window.geometry(f'{width}x{height}+{x}+{y}')
                
                # Header
                header = tk.Frame(details_window, bg='#17a2b8', height=60)
                header.pack(fill='x')
                tk.Label(header, text="Blood Request Details", font=('Arial', 16, 'bold'),
                        bg='#17a2b8', fg='white').pack(pady=15)
                
                # Details text
                text_frame = tk.Frame(details_window, padx=20, pady=20)
                text_frame.pack(fill='both', expand=True)
                
                text = tk.Text(text_frame, wrap='word', font=('Courier', 10), padx=10, pady=10)
                text.pack(fill='both', expand=True)
                text.insert('1.0', details)
                text.config(state='disabled')
                
                # Buttons
                btn_frame = tk.Frame(details_window, pady=15)
                btn_frame.pack()
                
                tk.Button(btn_frame, text="Accept Request", bg='#28a745', fg='white',
                         font=('Arial', 11, 'bold'), width=15,
                         command=lambda: [self.accept_request_from_details(match_id), details_window.destroy()]).pack(side='left', padx=10)
                
                tk.Button(btn_frame, text="Close", bg='#6c757d', fg='white',
                         font=('Arial', 11), width=10,
                         command=details_window.destroy).pack(side='left', padx=10)
            
        except Exception as e:
            print(f"Error viewing match details: {e}")
            messagebox.showerror("Error", f"Failed to load details: {str(e)}")
    
    def accept_request_from_details(self, match_id):
        """Accept request from details window"""
        try:
            DonorMatch.update_status(match_id, 'confirmed', 
                                    f"Donor {self.donor['name']} confirmed availability")
            messagebox.showinfo("Success", "Request accepted successfully!")
            self.load_matches()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to accept request: {str(e)}")
    
    def load_history(self):
        """Load donation history"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        try:
            history = Donor.get_donation_history(self.donor['donor_id'])
            
            for record in history:
                next_eligible = record.get('next_eligible_date')
                next_eligible_str = next_eligible.strftime('%Y-%m-%d') if next_eligible else 'N/A'
                
                donation_date = record.get('donation_date')
                donation_date_str = donation_date.strftime('%Y-%m-%d') if donation_date else 'N/A'
                
                self.history_tree.insert('', 'end', values=(
                    record.get('donation_id', 'N/A'),
                    donation_date_str,
                    record.get('hospital_name', 'N/A'),
                    record.get('units_donated', 'N/A'),
                    record.get('status', 'N/A'),
                    next_eligible_str
                ))
        except Exception as e:
            print(f"Error loading donation history: {e}")
    
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
