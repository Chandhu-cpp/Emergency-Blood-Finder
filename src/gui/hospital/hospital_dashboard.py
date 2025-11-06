
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from src.models.donor_match import DonorMatch
from src.models.blood_request import BloodRequest
from src.models.donation_record import DonationRecord
from src.models.hospital_staff import HospitalStaff

class HospitalDashboard:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.staff = None
        
        self.window = tk.Toplevel()
        self.window.title(f"Hospital Staff Dashboard - {user['user_name']}")
        self.window.geometry("1200x700")
        
        self.center_window()
        
        # Load staff info
        if not self.load_staff_info():
            messagebox.showerror("Error", "Staff profile not found. Please contact admin.")
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
    
    def load_staff_info(self):
        """Load hospital staff information"""
        try:
            staff = HospitalStaff.get_by_user_id(self.user['user_id'])
            if staff:
                self.staff = staff
                return True
            return False
        except Exception as e:
            print(f"Error loading staff info: {e}")
            return False
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg='#007bff', height=60)
        header_frame.pack(fill='x')
        
        tk.Label(
            header_frame,
            text=f"🏥 Hospital Dashboard - {self.staff.get('hospital_name', 'Hospital')}",
            font=('Arial', 18, 'bold'),
            bg='#007bff',
            fg='white'
        ).pack(pady=15)
        
        # Tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Confirmed Matches (Need Scheduling)
        confirmed_tab = tk.Frame(notebook)
        notebook.add(confirmed_tab, text='✅ Confirmed Matches')
        self.create_confirmed_tab(confirmed_tab)
        
        # Tab 2: Scheduled Donations (Need Completion)
        scheduled_tab = tk.Frame(notebook)
        notebook.add(scheduled_tab, text='📅 Scheduled Donations')
        self.create_scheduled_tab(scheduled_tab)
        
        # Tab 3: Completed Donations
        completed_tab = tk.Frame(notebook)
        notebook.add(completed_tab, text='✔️ Completed Donations')
        self.create_completed_tab(completed_tab)
    
    def create_confirmed_tab(self, parent):
        """Confirmed matches waiting to be scheduled"""
        frame = tk.Frame(parent, padx=10, pady=10)
        frame.pack(fill='both', expand=True)
        
        # Info label
        info_frame = tk.Frame(frame, bg='#d1ecf1', padx=10, pady=10)
        info_frame.pack(fill='x', pady=(0, 10))
        tk.Label(info_frame, text="ℹ️ These donors have confirmed their availability. Schedule their donation appointments.",
                font=('Arial', 10), bg='#d1ecf1', fg='#0c5460').pack()
        
        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="Refresh", bg='#007bff', fg='white', 
                 command=self.load_confirmed).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Schedule Donation", bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                 command=self.schedule_donation).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.confirmed_tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set,
                                          columns=('Match ID', 'Donor', 'Patient', 'Blood', 'Urgency', 'Units', 'Phone'),
                                          show='headings')
        
        scrollbar.config(command=self.confirmed_tree.yview)
        
        self.confirmed_tree.heading('Match ID', text='Match ID')
        self.confirmed_tree.heading('Donor', text='Donor Name')
        self.confirmed_tree.heading('Patient', text='Patient Name')
        self.confirmed_tree.heading('Blood', text='Blood Group')
        self.confirmed_tree.heading('Urgency', text='Urgency')
        self.confirmed_tree.heading('Units', text='Units')
        self.confirmed_tree.heading('Phone', text='Donor Phone')
        
        self.confirmed_tree.column('Match ID', width=80)
        self.confirmed_tree.column('Donor', width=150)
        self.confirmed_tree.column('Patient', width=150)
        self.confirmed_tree.column('Blood', width=80)
        self.confirmed_tree.column('Urgency', width=80)
        self.confirmed_tree.column('Units', width=60)
        self.confirmed_tree.column('Phone', width=120)
        
        self.confirmed_tree.pack(fill='both', expand=True)
        
        self.load_confirmed()
    
    def create_scheduled_tab(self, parent):
        """Scheduled donations waiting to be completed"""
        frame = tk.Frame(parent, padx=10, pady=10)
        frame.pack(fill='both', expand=True)
        
        # Info label
        info_frame = tk.Frame(frame, bg='#fff3cd', padx=10, pady=10)
        info_frame.pack(fill='x', pady=(0, 10))
        tk.Label(info_frame, text="📅 These donations are scheduled. Mark as completed after the donor donates.",
                font=('Arial', 10), bg='#fff3cd', fg='#856404').pack()
        
        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="Refresh", bg='#007bff', fg='white', 
                 command=self.load_scheduled).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Mark as Completed", bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                 command=self.complete_donation).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Cancel Donation", bg='#dc3545', fg='white',
                 command=self.cancel_donation).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.scheduled_tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set,
                                          columns=('Donation ID', 'Donor', 'Patient', 'Blood', 'Units', 'Date', 'Status'),
                                          show='headings')
        
        scrollbar.config(command=self.scheduled_tree.yview)
        
        self.scheduled_tree.heading('Donation ID', text='Donation ID')
        self.scheduled_tree.heading('Donor', text='Donor Name')
        self.scheduled_tree.heading('Patient', text='Patient Name')
        self.scheduled_tree.heading('Blood', text='Blood Group')
        self.scheduled_tree.heading('Units', text='Units')
        self.scheduled_tree.heading('Date', text='Scheduled Date')
        self.scheduled_tree.heading('Status', text='Status')
        
        self.scheduled_tree.pack(fill='both', expand=True)
        
        self.load_scheduled()
    
    def create_completed_tab(self, parent):
        """Completed donations history"""
        frame = tk.Frame(parent, padx=10, pady=10)
        frame.pack(fill='both', expand=True)
        
        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="Refresh", bg='#007bff', fg='white', 
                 command=self.load_completed).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.completed_tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set,
                                          columns=('Donation ID', 'Donor', 'Blood', 'Units', 'Date', 'Next Eligible'),
                                          show='headings')
        
        scrollbar.config(command=self.completed_tree.yview)
        
        self.completed_tree.heading('Donation ID', text='Donation ID')
        self.completed_tree.heading('Donor', text='Donor Name')
        self.completed_tree.heading('Blood', text='Blood Group')
        self.completed_tree.heading('Units', text='Units')
        self.completed_tree.heading('Date', text='Donation Date')
        self.completed_tree.heading('Next Eligible', text='Next Eligible')
        
        self.completed_tree.pack(fill='both', expand=True)
        
        self.load_completed()
    
    def load_confirmed(self):
        """Load confirmed matches"""
        for item in self.confirmed_tree.get_children():
            self.confirmed_tree.delete(item)
        
        try:
            # Debug: Print hospital_id
            print(f"DEBUG: Loading confirmed matches for hospital_id: {self.staff['hospital_id']}")
            
            matches = DonorMatch.get_confirmed_by_hospital(self.staff['hospital_id'])
            
            print(f"DEBUG: Found {len(matches)} confirmed matches")
            
            for match in matches:
                print(f"DEBUG: Match - {match}")
                self.confirmed_tree.insert('', 'end', values=(
                    match['match_id'],
                    match.get('donor_name', 'N/A'),
                    match.get('patient_name', 'N/A'),
                    match['blood_group_needed'],
                    match['urgency'],
                    match['units_needed'],
                    match.get('donor_phone', 'N/A')
                ))
                
            # Show count
            count = len(matches)
            if count == 0:
                messagebox.showinfo("No Matches", "No confirmed matches found for your hospital.")
            else:
                print(f"Loaded {count} confirmed matches")
                
        except Exception as e:
            print(f"Error loading confirmed matches: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load confirmed matches: {str(e)}")
    
    def load_scheduled(self):
        """Load scheduled donations"""
        for item in self.scheduled_tree.get_children():
            self.scheduled_tree.delete(item)
        
        try:
            donations = DonationRecord.get_scheduled_by_hospital(self.staff['hospital_id'])
            
            for donation in donations:
                donation_date = donation.get('donation_date')
                date_str = donation_date.strftime('%Y-%m-%d') if donation_date else 'N/A'
                
                self.scheduled_tree.insert('', 'end', values=(
                    donation['donation_id'],
                    donation['donor_name'],
                    donation.get('patient_name', 'N/A'),
                    donation['blood_group'],
                    donation['units_donated'],
                    date_str,
                    donation['status']
                ))
        except Exception as e:
            print(f"Error loading scheduled donations: {e}")
    
    def load_completed(self):
        """Load completed donations"""
        for item in self.completed_tree.get_children():
            self.completed_tree.delete(item)
        
        try:
            donations = DonationRecord.get_completed_by_hospital(self.staff['hospital_id'])
            
            for donation in donations:
                donation_date = donation.get('donation_date')
                date_str = donation_date.strftime('%Y-%m-%d') if donation_date else 'N/A'
                
                next_eligible = donation.get('next_eligible_date')
                next_str = next_eligible.strftime('%Y-%m-%d') if next_eligible else 'N/A'
                
                self.completed_tree.insert('', 'end', values=(
                    donation['donation_id'],
                    donation['donor_name'],
                    donation['blood_group'],
                    donation['units_donated'],
                    date_str,
                    next_str
                ))
        except Exception as e:
            print(f"Error loading completed donations: {e}")
    
    def schedule_donation(self):
        """Schedule a donation from confirmed match"""
        selected = self.confirmed_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a match to schedule")
            return
        
        item = self.confirmed_tree.item(selected[0])
        match_id = item['values'][0]
        donor_name = item['values'][1]
        units = item['values'][5]
        
        # Create scheduling window
        schedule_window = tk.Toplevel(self.window)
        schedule_window.title("Schedule Donation")
        schedule_window.geometry("400x300")
        schedule_window.resizable(False, False)
        
        # Center
        schedule_window.update_idletasks()
        width = schedule_window.winfo_width()
        height = schedule_window.winfo_height()
        x = (schedule_window.winfo_screenwidth() // 2) - (width // 2)
        y = (schedule_window.winfo_screenheight() // 2) - (height // 2)
        schedule_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Header
        header = tk.Frame(schedule_window, bg='#28a745', height=60)
        header.pack(fill='x')
        tk.Label(header, text="Schedule Donation Appointment", font=('Arial', 14, 'bold'),
                bg='#28a745', fg='white').pack(pady=15)
        
        # Form
        form_frame = tk.Frame(schedule_window, padx=30, pady=20)
        form_frame.pack()
        
        tk.Label(form_frame, text=f"Donor: {donor_name}", font=('Arial', 11)).pack(pady=5)
        tk.Label(form_frame, text=f"Units: {units}", font=('Arial', 11)).pack(pady=5)
        
        tk.Label(form_frame, text="Donation Date:", font=('Arial', 11, 'bold')).pack(pady=(15, 5))
        date_entry = DateEntry(form_frame, width=25, background='darkblue', 
                              foreground='white', borderwidth=2, 
                              date_pattern='yyyy-mm-dd', mindate=datetime.now().date())
        date_entry.pack(pady=5)
        
        def save_schedule():
            donation_date = date_entry.get_date()
            
            try:
                # Call stored procedure to confirm donation
                BloodRequest.confirm_donation(match_id, donation_date, units, self.staff['staff_id'])
                
                messagebox.showinfo("Success", f"Donation scheduled for {donation_date}!")
                schedule_window.destroy()
                self.load_confirmed()
                self.load_scheduled()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to schedule donation: {str(e)}")
        
        # Buttons
        btn_frame = tk.Frame(schedule_window, pady=20)
        btn_frame.pack()
        
        tk.Button(btn_frame, text="Schedule", bg='#28a745', fg='white',
                 font=('Arial', 12, 'bold'), width=12, command=save_schedule).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Cancel", bg='#6c757d', fg='white',
                 font=('Arial', 12), width=10, command=schedule_window.destroy).pack(side='left', padx=10)
    
    def complete_donation(self):
        """Mark donation as completed"""
        selected = self.scheduled_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a donation to complete")
            return
        
        item = self.scheduled_tree.item(selected[0])
        donation_id = item['values'][0]
        donor_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Completion",
                              f"Mark donation by {donor_name} as completed?\n\n"
                              f"This will:\n"
                              f"• Update blood inventory\n"
                              f"• Update donor's last donation date\n"
                              f"• Mark request as fulfilled"):
            try:
                # Update donation status to completed (Trigger will handle the rest!)
                DonationRecord.update_status(donation_id, 'completed')
                
                messagebox.showinfo("Success", 
                                   "Donation marked as completed! ✅\n\n"
                                   "• Inventory updated\n"
                                   "• Donor record updated\n"
                                   "• Request fulfilled")
                
                self.load_scheduled()
                self.load_completed()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to complete donation: {str(e)}")
    
    def cancel_donation(self):
        """Cancel a scheduled donation"""
        selected = self.scheduled_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a donation to cancel")
            return
        
        item = self.scheduled_tree.item(selected[0])
        donation_id = item['values'][0]
        
        if messagebox.askyesno("Confirm Cancellation", "Cancel this donation?"):
            try:
                DonationRecord.update_status(donation_id, 'cancelled')
                messagebox.showinfo("Success", "Donation cancelled")
                self.load_scheduled()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel donation: {str(e)}")
    
    def on_closing(self):
        self.window.destroy()
        self.parent.deiconify()

