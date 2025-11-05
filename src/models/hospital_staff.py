from src.config.database import db

class HospitalStaff:
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get hospital staff by user_id"""
        query = """
            SELECT hs.*, h.hospital_name, h.city
            FROM HOSPITAL_STAFF hs
            JOIN HOSPITAL h ON hs.hospital_id = h.hospital_id
            WHERE hs.user_id = %s
        """
        return db.fetch_one(query, (user_id,))