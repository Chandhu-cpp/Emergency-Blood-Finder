# Emergency Blood Finder System

## Team Details
- **Member 1:** CHANDISHWAR E (PES1UG23AM082)
- **Member 2:** CHARAN Y N (PES1UG23AM083)

## Project Overview
Emergency Blood Finder is a database-driven system designed to quickly connect patients 
in urgent need of blood with compatible donors using Python Tkinter GUI and MySQL database.

---

## Tech Stack
- **Frontend:** Python Tkinter (GUI)
- **Backend:** Python 3.8+
- **Database:** MySQL 8.0+
- **Libraries:** mysql-connector-python, python-dotenv, tkcalendar

---

## Installation Steps

### Step 1: Install Python Dependencies

```bash
# Navigate to project root
cd Emergency-Blood-Finder

# Install required packages
pip install -r requirements.txt
```

### Step 2: Setup MySQL Database

```bash
# Login to MySQL
mysql -u root -p

# Run the complete setup script
mysql -u root -p < database/complete_setup.sql
```

### Step 3: Configure Database Connection

Create `.env` file in project root:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=emergency_blood
DB_PORT=3306
```

### Step 4: Run the Application

```bash
# From project root
python run.py
```

---

## Test Login Credentials

### Patient Login:
- Email: `rahul.sharma@example.com`
- Role: Patient

### Donor Login:
- Email: `priya.patel@example.com`
- Role: Donor

### Admin Login:
- Email: `admin@emergency.com`
- Role: Admin

---

## Features Implemented

### CRUD Operations
- **CREATE:** Add blood requests, users, donors
- **READ:** View requests, donation history, inventory
- **UPDATE:** Update availability, request status
- **DELETE:** Cancel requests, delete users

### Database Components
- **Tables:** 10 tables (USER, DONOR, PATIENT, HOSPITAL, etc.)
- **Triggers:** 3 triggers (auto-match, prevent early donation, update inventory)
- **Procedures:** 3 procedures (match donor, confirm donation, complete donation)
- **Functions:** 1 function (check donor eligibility)
- **Queries:** Nested, Join, Aggregate queries

### User Roles
1. **Patient:** Create blood requests, view status, search donors
2. **Donor:** Update availability, view donation history
3. **Admin:** User management, view statistics, manage inventory
4. **Hospital Staff:** Views donation requests and schedules the donation

---

## Taking Screenshots

### For CRUD Operations:
1. Run the application
2. Login as different users
3. Perform CREATE, READ, UPDATE, DELETE operations
4. Take screenshots of each operation
5. Save to `screenshots/crud_operations/` folder

### For Dashboards:
1. Login to each role (Patient, Donor, Admin)
2. Take full-screen screenshots
3. Save to `screenshots/dashboards/` folder

---

## Project Structure

```
Emergency-Blood-Finder/
├── database/              # All SQL files
├── src/                   # Application source code
│   ├── config/           # Database connection
│   ├── models/           # Data models
│   ├── gui/              # GUI components
│   └── utils/            # Helper functions
├── screenshots/          # Documentation screenshots
├── docs/                 # Project documentation
├── requirements.txt      # Python dependencies
├── .env                  # Database credentials (don't push!)
└── run.py               # Application launcher
```

---

## How It Works

### Complete Workflow:

1. **Patient creates blood request** 
   → Trigger automatically matches available donor
   → Creates entry in DONOR_MATCH table

2. **Hospital staff confirms donation**
   → Calls stored procedure sp_Confirm_Donation
   → Creates DONATION_RECORD

3. **After donation completes**
   → Trigger updates donor's last_donation_date
   → Updates blood inventory
   → Updates request status to 'fulfilled'

---


## Troubleshooting

### Error: "Can't connect to MySQL server"
- Check if MySQL is running
- Verify credentials in .env file
- Check DB_HOST and DB_PORT

### Error: "Table doesn't exist"
- Run database/complete_setup.sql
- Verify database name in .env

### Error: "Module not found"
- Run: `pip install -r requirements.txt`
- Make sure you're in correct directory

---

## Contact
For any queries, contact team members

---

## License
MIT License
