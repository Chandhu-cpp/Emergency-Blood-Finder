from src.config.database import db

class Hospital:
    
    @staticmethod
    def get_all():
        """Get all hospitals"""
        query = "SELECT * FROM HOSPITAL WHERE is_active = TRUE ORDER BY hospital_name"
        return db.fetch_all(query)
    
    @staticmethod
    def get_by_id(hospital_id):
        """Get hospital by ID"""
        query = "SELECT * FROM HOSPITAL WHERE hospital_id = %s"
        return db.fetch_one(query, (hospital_id,))