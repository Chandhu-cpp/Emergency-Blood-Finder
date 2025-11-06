# ============================================
# FILE: check_flow.py (Create in root folder)
# Diagnostic script to check the complete flow
# ============================================

from src.config.database import db

# Connect to database
db.connect()

print("=" * 60)
print("DIAGNOSTIC: Blood Request Flow Check")
print("=" * 60)

# 1. Check all blood requests
print("\n1. ALL BLOOD REQUESTS:")
print("-" * 60)
requests_query = """
    SELECT 
        br.request_id,
        br.user_id,
        p.name as patient_name,
        br.blood_group_needed,
        br.urgency,
        br.status,
        br.hospital_id,
        h.hospital_name
    FROM BLOOD_REQUEST br
    LEFT JOIN PATIENT p ON br.user_id = p.user_id
    LEFT JOIN HOSPITAL h ON br.hospital_id = h.hospital_id
    ORDER BY br.request_id DESC
    LIMIT 10
"""
requests = db.fetch_all(requests_query)
for req in requests:
    print(f"  Request ID: {req['request_id']}, Patient: {req.get('patient_name', 'NO NAME')}, "
          f"Blood: {req['blood_group_needed']}, Status: {req['status']}, "
          f"Hospital: {req.get('hospital_name', 'NO HOSPITAL')}")

# 2. Check all donor matches
print("\n2. ALL DONOR MATCHES:")
print("-" * 60)
matches_query = """
    SELECT 
        dm.match_id,
        dm.request_id,
        dm.donor_id,
        d.name as donor_name,
        dm.match_status,
        br.hospital_id
    FROM DONOR_MATCH dm
    JOIN DONOR d ON dm.donor_id = d.donor_id
    JOIN BLOOD_REQUEST br ON dm.request_id = br.request_id
    ORDER BY dm.match_id DESC
    LIMIT 10
"""
matches = db.fetch_all(matches_query)
for match in matches:
    print(f"  Match ID: {match['match_id']}, Request: {match['request_id']}, "
          f"Donor: {match.get('donor_name', 'NO NAME')}, Status: {match['match_status']}, "
          f"Hospital: {match['hospital_id']}")

# 3. Check confirmed matches for Apollo Hospital (hospital_id = 1)
print("\n3. CONFIRMED MATCHES FOR APOLLO HOSPITAL (hospital_id=1):")
print("-" * 60)
confirmed_query = """
    SELECT 
        dm.match_id,
        dm.match_status,
        d.name as donor_name,
        d.phone as donor_phone,
        br.blood_group_needed,
        br.urgency,
        br.units_needed,
        br.status as request_status,
        br.hospital_id,
        p.name as patient_name
    FROM DONOR_MATCH dm
    JOIN DONOR d ON dm.donor_id = d.donor_id
    JOIN BLOOD_REQUEST br ON dm.request_id = br.request_id
    LEFT JOIN PATIENT p ON br.user_id = p.user_id
    WHERE br.hospital_id = 1
    AND dm.match_status = 'confirmed'
    ORDER BY dm.match_id DESC
"""
confirmed = db.fetch_all(confirmed_query)
print(f"  Found {len(confirmed)} confirmed matches")
for conf in confirmed:
    print(f"  Match ID: {conf['match_id']}, Donor: {conf.get('donor_name', 'NO NAME')}, "
          f"Patient: {conf.get('patient_name', 'NO NAME')}, Status: {conf['match_status']}, "
          f"Request Status: {conf['request_status']}")

# 4. Check hospital staff
print("\n4. HOSPITAL STAFF:")
print("-" * 60)
staff_query = """
    SELECT 
        hs.staff_id,
        hs.user_id,
        hs.hospital_id,
        hs.name,
        h.hospital_name
    FROM HOSPITAL_STAFF hs
    JOIN HOSPITAL h ON hs.hospital_id = h.hospital_id
"""
staff = db.fetch_all(staff_query)
for s in staff:
    print(f"  Staff ID: {s['staff_id']}, Name: {s['name']}, "
          f"Hospital: {s['hospital_name']} (ID: {s['hospital_id']})")

# 5. Check donation records
print("\n5. DONATION RECORDS:")
print("-" * 60)
donations_query = """
    SELECT 
        dr.donation_id,
        dr.donor_id,
        d.name as donor_name,
        dr.hospital_id,
        dr.status,
        dr.donation_date
    FROM DONATION_RECORD dr
    JOIN DONOR d ON dr.donor_id = d.donor_id
    ORDER BY dr.donation_id DESC
    LIMIT 10
"""
donations = db.fetch_all(donations_query)
print(f"  Found {len(donations)} donation records")
for don in donations:
    print(f"  Donation ID: {don['donation_id']}, Donor: {don.get('donor_name', 'NO NAME')}, "
          f"Hospital: {don['hospital_id']}, Status: {don['status']}, Date: {don.get('donation_date', 'NO DATE')}")

# 6. Summary
print("\n" + "=" * 60)
print("SUMMARY:")
print("=" * 60)
print(f"Total Blood Requests: {len(requests)}")
print(f"Total Donor Matches: {len(matches)}")
print(f"Confirmed Matches for Apollo: {len(confirmed)}")
print(f"Total Donation Records: {len(donations)}")

# 7. Check for issues
print("\n" + "=" * 60)
print("POTENTIAL ISSUES:")
print("=" * 60)

# Check for requests without patient names
no_patient = [r for r in requests if not r.get('patient_name')]
if no_patient:
    print(f"⚠️  {len(no_patient)} requests have no patient name!")
    for r in no_patient:
        print(f"    Request ID {r['request_id']}, user_id: {r['user_id']}")
        # Check if patient exists
        patient_check = db.fetch_one("SELECT * FROM PATIENT WHERE user_id = %s", (r['user_id'],))
        if not patient_check:
            print(f"    ❌ No PATIENT record found for user_id {r['user_id']}")
        else:
            print(f"    ✅ PATIENT record exists: {patient_check.get('name', 'NO NAME')}")

# Check for matches without donor names
no_donor = [m for m in matches if not m.get('donor_name')]
if no_donor:
    print(f"⚠️  {len(no_donor)} matches have no donor name!")

# Check confirmed matches not showing up
if len(matches) > 0 and len(confirmed) == 0:
    print("⚠️  There are matches but none are confirmed for Apollo Hospital!")
    print("    Check match_status values and hospital_id in requests")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)

db.disconnect()