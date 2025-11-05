from src.config.database import db

class DonorMatch:
    
    @staticmethod
    def get_by_donor_id(donor_id):
        """Get all matches for a specific donor"""
        query = """
            SELECT 
                dm.*,
                br.blood_group_needed,
                br.urgency,
                br.units_needed,
                br.medical_reason,
                br.request_date,
                br.required_by_date,
                p.name as patient_name,
                h.hospital_name,
                h.phone as hospital_phone,
                h.city
            FROM DONOR_MATCH dm
            JOIN BLOOD_REQUEST br ON dm.request_id = br.request_id
            JOIN PATIENT p ON br.user_id = p.user_id
            JOIN HOSPITAL h ON br.hospital_id = h.hospital_id
            WHERE dm.donor_id = %s
            ORDER BY dm.match_date DESC
        """
        return db.fetch_all(query, (donor_id,))
    
    @staticmethod
    def get_by_id(match_id):
        """Get single match by ID"""
        query = """
            SELECT 
                dm.*,
                br.blood_group_needed,
                br.urgency,
                br.units_needed,
                br.medical_reason,
                br.request_date,
                br.required_by_date,
                p.name as patient_name,
                h.hospital_name,
                h.phone as hospital_phone,
                h.city
            FROM DONOR_MATCH dm
            JOIN BLOOD_REQUEST br ON dm.request_id = br.request_id
            JOIN PATIENT p ON br.user_id = p.user_id
            JOIN HOSPITAL h ON br.hospital_id = h.hospital_id
            WHERE dm.match_id = %s
        """
        return db.fetch_one(query, (match_id,))
    
    @staticmethod
    def update_status(match_id, new_status, notes=None):
        """Update match status"""
        if notes:
            query = """
                UPDATE DONOR_MATCH 
                SET match_status = %s, notes = %s 
                WHERE match_id = %s
            """
            db.execute_query(query, (new_status, notes, match_id))
        else:
            query = """
                UPDATE DONOR_MATCH 
                SET match_status = %s 
                WHERE match_id = %s
            """
            db.execute_query(query, (new_status, match_id))
    
    @staticmethod
    def get_all():
        """Get all matches"""
        query = """
            SELECT 
                dm.*,
                d.name as donor_name,
                br.blood_group_needed,
                p.name as patient_name
            FROM DONOR_MATCH dm
            JOIN DONOR d ON dm.donor_id = d.donor_id
            JOIN BLOOD_REQUEST br ON dm.request_id = br.request_id
            JOIN PATIENT p ON br.user_id = p.user_id
            ORDER BY dm.match_date DESC
        """
        return db.fetch_all(query)
    
    @staticmethod
    def get_confirmed_by_hospital(hospital_id):
        """Get confirmed matches for a hospital"""
        query = """
            SELECT 
                dm.*,
                d.name as donor_name,
                d.phone as donor_phone,
                br.blood_group_needed,
                br.urgency,
                br.units_needed,
                p.name as patient_name
            FROM DONOR_MATCH dm
            JOIN DONOR d ON dm.donor_id = d.donor_id
            JOIN BLOOD_REQUEST br ON dm.request_id = br.request_id
            JOIN PATIENT p ON br.user_id = p.user_id
            WHERE br.hospital_id = %s 
            AND dm.match_status = 'confirmed'
            AND br.status = 'pending'
            ORDER BY br.urgency DESC, dm.match_date ASC
        """
        return db.fetch_all(query, (hospital_id,))