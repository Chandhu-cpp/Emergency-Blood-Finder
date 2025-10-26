from src.config.database import db

class User:
    
    @staticmethod
    def create(user_name, email, phone, role, password_hash=None):
        """Create new user"""
        query = """
            INSERT INTO USER (user_name, email, phone, role, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
        """
        return db.execute_query(query, (user_name, email, phone, role))
    
    @staticmethod
    def authenticate(email, role):
        """Simple authentication (you can add password later)"""
        query = """
            SELECT * FROM USER 
            WHERE email = %s AND role = %s AND is_active = TRUE
        """
        return db.fetch_one(query, (email, role))
    
    @staticmethod
    def get_all():
        """Get all users"""
        query = "SELECT * FROM USER ORDER BY created_at DESC"
        return db.fetch_all(query)
    
    @staticmethod
    def get_by_role(role):
        """Get users by role"""
        query = "SELECT * FROM USER WHERE role = %s"
        return db.fetch_all(query, (role,))
    
    @staticmethod
    def update(user_id, user_name, email, phone):
        """Update user"""
        query = """
            UPDATE USER 
            SET user_name = %s, email = %s, phone = %s
            WHERE user_id = %s
        """
        db.execute_query(query, (user_name, email, phone, user_id))
    
    @staticmethod
    def delete(user_id):
        """Delete user"""
        query = "DELETE FROM USER WHERE user_id = %s"
        db.execute_query(query, (user_id,))