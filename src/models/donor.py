from src.config.database import db

class Donor:
    
    @staticmethod
    def create(user_id, name, blood_group, city_pincode, weight):
        """Create new donor"""
        query = """
            INSERT INTO DONOR 
            (user_id, name, blood_group, city_pincode, is_available, weight)
            VALUES (%s, %s, %s, %s, TRUE, %s)
        """
        params = (user_id, name, blood_group, city_pincode, weight)
        return db.execute_query(query, params)
    
    @staticmethod
    def get_all():
        """Get all donors"""
        query = """
            SELECT d.*, u.email, u.phone
            FROM DONOR d
            JOIN USER u ON d.user_id = u.user_id
            ORDER BY d.name
        """
        return db.fetch_all(query)
    
    @staticmethod
    def get_by_id(donor_id):
        """Get donor by ID"""
        query = """
            SELECT d.*, u.email, u.phone
            FROM DONOR d
            JOIN USER u ON d.user_id = u.user_id
            WHERE d.donor_id = %s
        """
        return db.fetch_one(query, (donor_id,))
    
    @staticmethod
    def get_available(blood_group=None):
        """Get available donors"""
        if blood_group:
            query = """
                SELECT d.*, u.phone
                FROM DONOR d
                JOIN USER u ON d.user_id = u.user_id
                WHERE d.is_available = TRUE 
                AND d.blood_group = %s
                AND (d.last_donation_date IS NULL 
                     OR DATEDIFF(CURDATE(), d.last_donation_date) >= 90)
            """
            return db.fetch_all(query, (blood_group,))
        else:
            query = """
                SELECT d.*, u.phone
                FROM DONOR d
                JOIN USER u ON d.user_id = u.user_id
                WHERE d.is_available = TRUE
                AND (d.last_donation_date IS NULL 
                     OR DATEDIFF(CURDATE(), d.last_donation_date) >= 90)
            """
            return db.fetch_all(query)
    
    @staticmethod
    def update_availability(donor_id, is_available):
        """Update donor availability"""
        query = "UPDATE DONOR SET is_available = %s WHERE donor_id = %s"
        db.execute_query(query, (is_available, donor_id))
    
    @staticmethod
    def update(donor_id, name, blood_group, city_pincode, weight):
        """Update donor information"""
        query = """
            UPDATE DONOR 
            SET name = %s, blood_group = %s, city_pincode = %s, weight = %s
            WHERE donor_id = %s
        """
        db.execute_query(query, (name, blood_group, city_pincode, weight, donor_id))
    
    @staticmethod
    def delete(donor_id):
        """Delete donor"""
        query = "DELETE FROM DONOR WHERE donor_id = %s"
        db.execute_query(query, (donor_id,))
    
    @staticmethod
    def get_donation_history(donor_id):
        """Get donation history for a donor"""
        query = """
            SELECT 
                dr.*,
                h.hospital_name,
                br.medical_reason
            FROM DONATION_RECORD dr
            JOIN HOSPITAL h ON dr.hospital_id = h.hospital_id
            JOIN BLOOD_REQUEST br ON dr.request_id = br.request_id
            WHERE dr.donor_id = %s
            ORDER BY dr.donation_date DESC
        """
        return db.fetch_all(query, (donor_id,))