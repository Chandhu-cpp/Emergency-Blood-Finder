import tkinter as tk
from tkinter import ttk, messagebox
from src.models.user import User
from src.models.donor import Donor
from src.models.blood_request import BloodRequest
from src.models.blood_inventory import BloodInventory

class AdminDashboard:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.window = tk.Toplevel()
        self.window.title(f"Admin Dashboard - {user['user_name']}")
        self.window.geometry("1200x700")
        
        self.center_window()
        self.create_widgets()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.window, bg='#6f42c1', height=60)
        header_frame.pack(fill='x')
        
        tk.Label(
            header_frame,
            text=f"👨‍💼 Admin Dashboard - {self.user['user_name']}",
            font=('Arial', 18, 'bold'),
            bg='#6f42c1',
            fg='white'
        ).pack(pady=15)
        
        # Notebook (Tabs)
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Statistics
        stats_tab = tk.Frame(notebook)
        notebook.add(stats_tab, text='📊 Statistics')
        self.create_stats_tab(stats_tab)
        
        # Tab 2: User Management
        users_tab = tk.Frame(notebook)
        notebook.add(users_tab, text='👥 Users')
        self.create_users_tab(users_tab)
        
        # Tab 3: Blood Inventory
        inventory_tab = tk.Frame(notebook)
        notebook.add(inventory_tab, text='🩸 Blood Inventory')
        self.create_inventory_tab(inventory_tab)
        
        # Tab 4: Requests
        requests_tab = tk.Frame(notebook)
        notebook.add(requests_tab, text='📋 Blood Requests')
        self.create_requests_tab(requests_tab)
    
    def create_stats_tab(self, parent):
        """Statistics Dashboard"""
        # Get statistics
        users = User.get_all()
        donors = Donor.get_all()
        requests = BloodRequest.get_all()
        inventory = BloodInventory.get_all()
        
        total_users = len(users)
        total_donors = len(donors)
        available_donors = len([d for d in donors if d['is_available']])
        total_requests = len(requests)
        pending_requests = len([r for r in requests if r['status'] == 'pending'])
        fulfilled_requests = len([r for r in requests if r['status'] == 'fulfilled'])
        
        # Stats Frame
        stats_frame = tk.Frame(parent, padx=20, pady=20)
        stats_frame.pack(fill='both', expand=True)
        
        # Create stat cards
        row = 0
        col = 0
        
        stats = [
            ("Total Users", total_users, "#007bff"),
            ("Total Donors", total_donors, "#28a745"),
            ("Available Donors", available_donors, "#17a2b8"),
            ("Total Requests", total_requests, "#ffc107"),
            ("Pending Requests", pending_requests, "#dc3545"),
            ("Fulfilled Requests", fulfilled_requests, "#28a745"),
        ]
        
        for title, value, color in stats:
            card = tk.Frame(stats_frame, bg=color, padx=30, pady=20)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            tk.Label(card, text=str(value), font=('Arial', 36, 'bold'), bg=color, fg='white').pack()
            tk.Label(card, text=title, font=('Arial', 12), bg=color, fg='white').pack()
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Blood Inventory Summary
        inv_frame = tk.LabelFrame(stats_frame, text="Blood Inventory Summary", font=('Arial', 12, 'bold'), padx=10, pady=10)
        inv_frame.grid(row=row+1, column=0, columnspan=3, sticky='ew', pady=20)
        
        tree = ttk.Treeview(inv_frame, columns=('Hospital', 'Blood', 'Available', 'Reserved', 'Status'), show='headings', height=8)
        
        tree.heading('Hospital', text='Hospital')
        tree.heading('Blood', text='Blood Group')
        tree.heading('Available', text='Available')
        tree.heading('Reserved', text='Reserved')
        tree.heading('Status', text='Status')
        
        for item in inventory:
            tree.insert('', 'end', values=(
                item['hospital_name'],
                item['blood_group'],
                item['units_available'],
                item['units_reserved'],
                item['stock_status']
            ))
        
        tree.pack(fill='both', expand=True)
    
    def create_users_tab(self, parent):
        """User Management Tab"""
        frame = tk.Frame(parent, padx=10, pady=10)
        frame.pack(fill='both', expand=True)
        
        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="Refresh", bg='#007bff', fg='white', command=self.load_users).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Add User", bg='#28a745', fg='white', command=self.add_user).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Delete User", bg='#dc3545', fg='white', command=self.delete_user).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.users_tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set,
                                       columns=('ID', 'Name', 'Email', 'Phone', 'Role', 'Active', 'Created'), show='headings')
        
        scrollbar.config(command=self.users_tree.yview)
        
        self.users_tree.heading('ID', text='User ID')
        self.users_tree.heading('Name', text='Name')
        self.users_tree.heading('Email', text='Email')
        self.users_tree.heading('Phone', text='Phone')
        self.users_tree.heading('Role', text='Role')
        self.users_tree.heading('Active', text='Active')
        self.users_tree.heading('Created', text='Created Date')
        
        self.users_tree.column('ID', width=70)
        self.users_tree.column('Name', width=150)
        self.users_tree.column('Email', width=200)
        self.users_tree.column('Phone', width=120)
        self.users_tree.column('Role', width=120)
        self.users_tree.column('Active', width=70)
        self.users_tree.column('Created', width=150)
        
        self.users_tree.pack(fill='both', expand=True)
        
        self.load_users()
    
    def load_users(self):
        """Load all users"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        users = User.get_all()
        for user in users:
            self.users_tree.insert('', 'end', values=(
                user['user_id'],
                user['user_name'],
                user['email'],
                user['phone'],
                user['role'],
                'Yes' if user['is_active'] else 'No',
                user['created_at'].strftime('%Y-%m-%d %H:%M') if user['created_at'] else ''
            ))
    
    def add_user(self):
        """Add new user"""
        add_window = tk.Toplevel(self.window)
        add_window.title("Add New User")
        add_window.geometry("400x350")
        
        tk.Label(add_window, text="Add New User", font=('Arial', 14, 'bold')).pack(pady=10)
        
        form_frame = tk.Frame(add_window, padx=20, pady=10)
        form_frame.pack()
        
        tk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky='w', pady=5)
        email_entry = tk.Entry(form_frame, width=30)
        email_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky='w', pady=5)
        phone_entry = tk.Entry(form_frame, width=30)
        phone_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(form_frame, text="Role:").grid(row=3, column=0, sticky='w', pady=5)
        role_var = tk.StringVar(value='patient')
        role_combo = ttk.Combobox(form_frame, textvariable=role_var, 
                                  values=['patient', 'donor', 'hospital_staff', 'admin'], 
                                  state='readonly', width=27)
        role_combo.grid(row=3, column=1, pady=5)
        
        def save_user():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            role = role_var.get()
            
            if not all([name, email, phone]):
                messagebox.showerror("Error", "All fields are required")
                return
            
            try:
                User.create(name, email, phone, role)
                messagebox.showinfo("Success", "User created successfully")
                self.load_users()
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create user: {str(e)}")
        
        tk.Button(add_window, text="Save User", bg='#28a745', fg='white', 
                 command=save_user, width=15).pack(pady=20)
    
    def delete_user(self):
        """Delete selected user"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        item = self.users_tree.item(selected[0])
        user_id = item['values'][0]
        user_name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete user '{user_name}'?\nThis will cascade delete all related records!"):
            try:
                User.delete(user_id)
                messagebox.showinfo("Success", "User deleted successfully")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
    
    def create_inventory_tab(self, parent):
        """Blood Inventory Tab"""
        frame = tk.Frame(parent, padx=10, pady=10)
        frame.pack(fill='both', expand=True)
        
        tk.Button(frame, text="Refresh", bg='#007bff', fg='white', 
                 command=self.load_inventory).pack(pady=5)
        
        # Treeview
        self.inv_tree = ttk.Treeview(frame, columns=('ID', 'Hospital', 'Blood', 'Available', 'Reserved', 'Threshold', 'Status', 'Updated'), 
                                     show='headings')
        
        self.inv_tree.heading('ID', text='Inv ID')
        self.inv_tree.heading('Hospital', text='Hospital')
        self.inv_tree.heading('Blood', text='Blood Group')
        self.inv_tree.heading('Available', text='Available')
        self.inv_tree.heading('Reserved', text='Reserved')
        self.inv_tree.heading('Threshold', text='Threshold')
        self.inv_tree.heading('Status', text='Status')
        self.inv_tree.heading('Updated', text='Last Updated')
        
        self.inv_tree.pack(fill='both', expand=True, pady=10)
        
        self.load_inventory()
    
    def load_inventory(self):
        """Load blood inventory"""
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        inventory = BloodInventory.get_all()
        for item in inventory:
            self.inv_tree.insert('', 'end', values=(
                item['inventory_id'],
                item['hospital_name'],
                item['blood_group'],
                item['units_available'],
                item['units_reserved'],
                item['threshold'],
                item['stock_status'],
                item['last_updated'].strftime('%Y-%m-%d %H:%M') if item['last_updated'] else ''
            ))
    
    def create_requests_tab(self, parent):
        """Blood Requests Tab"""
        frame = tk.Frame(parent, padx=10, pady=10)
        frame.pack(fill='both', expand=True)
        
        tk.Button(frame, text="Refresh", bg='#007bff', fg='white', 
                 command=self.load_requests).pack(pady=5)
        
        # Treeview
        self.req_tree = ttk.Treeview(frame, columns=('ID', 'Patient', 'Blood', 'Urgency', 'Status', 'Units', 'Donor', 'Date'), 
                                     show='headings')
        
        self.req_tree.heading('ID', text='Req ID')
        self.req_tree.heading('Patient', text='Patient')
        self.req_tree.heading('Blood', text='Blood Group')
        self.req_tree.heading('Urgency', text='Urgency')
        self.req_tree.heading('Status', text='Status')
        self.req_tree.heading('Units', text='Units')
        self.req_tree.heading('Donor', text='Matched Donor')
        self.req_tree.heading('Date', text='Request Date')
        
        self.req_tree.pack(fill='both', expand=True, pady=10)
        
        self.load_requests()
    
    def load_requests(self):
        """Load blood requests"""
        for item in self.req_tree.get_children():
            self.req_tree.delete(item)
        
        requests = BloodRequest.get_all()
        for req in requests:
            self.req_tree.insert('', 'end', values=(
                req['request_id'],
                req.get('patient_name', 'N/A'),
                req['blood_group_needed'],
                req['urgency'],
                req['status'],
                req['units_needed'],
                req.get('donor_name', 'Not Matched'),
                req['request_date'].strftime('%Y-%m-%d %H:%M') if req['request_date'] else ''
            ))
    
    def on_closing(self):
        self.window.destroy()
        self.parent.deiconify()