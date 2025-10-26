from src.config.database import db

class BloodRequest:
    
    @staticmethod
    def create(user_id, hospital_id, blood_group, urgency, units_needed, medical_reason, required_by_date):
        """Create new blood request (Trigger will auto-match donor)"""
        query = """
            INSERT INTO BLOOD_REQUEST 
            (user_id, hospital_id, blood_group_needed, urgency, status, 
             units_needed, medical_reason, required_by_date)
            VALUES (%s, %s, %s, %s, 'pending', %s, %s, %s)
        """
        params = (user_id, hospital_id, blood_group, urgency, units_needed, 
                 medical_reason, required_by_date)
        request_id = db.execute_query(query, params)
        
        # Check if donor was matched (by trigger)
        match = BloodRequest.get_match(request_id)
        
        return {
            'request_id': request_id,
            'match': match
        }
    
    @staticmethod
    def get_all():
        """Get all blood requests with details"""
        query = """
            SELECT 
                br.request_id,
                br.blood_group_needed,
                br.urgency,
                br.status,
                br.units_needed,
                br.medical_reason,
                br.request_date,
                br.required_by_date,
                p.name as patient_name,
                h.hospital_name,
                dm.match_id,
                d.name as donor_name,
                dm.match_status
            FROM BLOOD_REQUEST br
            LEFT JOIN PATIENT p ON br.user_id = p.user_id
            LEFT JOIN HOSPITAL h ON br.hospital_id = h.hospital_id
            LEFT JOIN DONOR_MATCH dm ON br.request_id = dm.request_id
            LEFT JOIN DONOR d ON dm.donor_id = d.donor_id
            ORDER BY br.request_date DESC
        """
        return db.fetch_all(query)
    
    @staticmethod
    def get_by_id(request_id):
        """Get single blood request"""
        query = """
            SELECT br.*, p.name as patient_name, h.hospital_name
            FROM BLOOD_REQUEST br
            LEFT JOIN PATIENT p ON br.user_id = p.user_id
            LEFT JOIN HOSPITAL h ON br.hospital_id = h.hospital_id
            WHERE br.request_id = %s
        """
        return db.fetch_one(query, (request_id,))
    
    @staticmethod
    def get_pending():
        """Get all pending requests"""
        query = """
            SELECT 
                br.*,
                p.name as patient_name,
                dm.match_id,
                d.name as donor_name
            FROM BLOOD_REQUEST br
            LEFT JOIN PATIENT p ON br.user_id = p.user_id
            LEFT JOIN DONOR_MATCH dm ON br.request_id = dm.request_id
            LEFT JOIN DONOR d ON dm.donor_id = d.donor_id
            WHERE br.status = 'pending'
            ORDER BY br.urgency DESC, br.request_date
        """
        return db.fetch_all(query)
    
    @staticmethod
    def update_status(request_id, new_status):
        """Update request status"""
        query = "UPDATE BLOOD_REQUEST SET status = %s WHERE request_id = %s"
        db.execute_query(query, (new_status, request_id))
    
    @staticmethod
    def delete(request_id):
        """Delete blood request"""
        query = "DELETE FROM BLOOD_REQUEST WHERE request_id = %s"
        db.execute_query(query, (request_id,))
    
    @staticmethod
    def get_match(request_id):
        """Get matched donor for a request"""
        query = """
            SELECT dm.*, d.name, d.phone, d.blood_group
            FROM DONOR_MATCH dm
            JOIN DONOR d ON dm.donor_id = d.donor_id
            WHERE dm.request_id = %s
        """
        return db.fetch_one(query, (request_id,))
    
    @staticmethod
    def confirm_donation(match_id, donation_date, units_donated, conducted_by):
        """Confirm donation using stored procedure"""
        try:
            results = db.call_procedure('sp_Confirm_Donation', 
                                       [match_id, donation_date, units_donated, conducted_by])
            return True
        except Exception as e:
            print(f"Error confirming donation: {e}")
            return False