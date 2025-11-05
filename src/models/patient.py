from src.config.database import db

class Patient:
    
    @staticmethod
    def create(user_id, name, blood_group, city_pincode, emergency_contact, medical_history=''):
        """Create new patient profile"""
        query = """
            INSERT INTO PATIENT 
            (user_id, name, blood_group, city_pincode, emergency_contact, medical_history)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return db.execute_query(query, (user_id, name, blood_group, city_pincode, emergency_contact, medical_history))
    
    @staticmethod
    def get_by_user_id(user_id):
        """Check if patient profile exists for user"""
        query = "SELECT * FROM PATIENT WHERE user_id = %s"
        return db.fetch_one(query, (user_id,))
    
    @staticmethod
    def get_all():
        """Get all patients"""
        query = """
            SELECT p.*, u.email, u.phone
            FROM PATIENT p
            JOIN USER u ON p.user_id = u.user_id
            ORDER BY p.name
        """
        return db.fetch_all(query)
    
    @staticmethod
    def update(patient_id, name, blood_group, city_pincode, emergency_contact, medical_history):
        """Update patient information"""
        query = """
            UPDATE PATIENT 
            SET name = %s, blood_group = %s, city_pincode = %s, 
                emergency_contact = %s, medical_history = %s
            WHERE patient_id = %s
        """
        db.execute_query(query, (name, blood_group, city_pincode, emergency_contact, medical_history, patient_id))