from src.config.database import db

class DonationRecord:
    
    @staticmethod
    def get_scheduled_by_hospital(hospital_id):
        """Get scheduled donations for a hospital"""
        query = """
            SELECT 
                dr.*,
                d.name as donor_name,
                p.name as patient_name
            FROM DONATION_RECORD dr
            JOIN DONOR d ON dr.donor_id = d.donor_id
            LEFT JOIN BLOOD_REQUEST br ON dr.request_id = br.request_id
            LEFT JOIN PATIENT p ON br.user_id = p.user_id
            WHERE dr.hospital_id = %s 
            AND dr.status = 'scheduled'
            ORDER BY dr.donation_date ASC
        """
        return db.fetch_all(query, (hospital_id,))
    
    @staticmethod
    def get_completed_by_hospital(hospital_id):
        """Get completed donations for a hospital"""
        query = """
            SELECT 
                dr.*,
                d.name as donor_name
            FROM DONATION_RECORD dr
            JOIN DONOR d ON dr.donor_id = d.donor_id
            WHERE dr.hospital_id = %s 
            AND dr.status = 'completed'
            ORDER BY dr.donation_date DESC
            LIMIT 50
        """
        return db.fetch_all(query, (hospital_id,))
    
    @staticmethod
    def update_status(donation_id, new_status):
        """Update donation status"""
        query = "UPDATE DONATION_RECORD SET status = %s WHERE donation_id = %s"
        db.execute_query(query, (new_status, donation_id))
        