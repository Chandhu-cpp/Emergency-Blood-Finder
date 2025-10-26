from src.config.database import db

class BloodInventory:
    
    @staticmethod
    def get_by_hospital(hospital_id):
        """Get inventory for a hospital"""
        query = """
            SELECT * FROM BLOOD_INVENTORY
            WHERE hospital_id = %s
            ORDER BY blood_group
        """
        return db.fetch_all(query, (hospital_id,))
    
    @staticmethod
    def get_all():
        """Get all inventory with hospital names"""
        query = """
            SELECT 
                bi.*,
                h.hospital_name,
                CASE 
                    WHEN bi.units_available <= bi.threshold THEN 'LOW STOCK'
                    ELSE 'SUFFICIENT'
                END as stock_status
            FROM BLOOD_INVENTORY bi
            JOIN HOSPITAL h ON bi.hospital_id = h.hospital_id
            ORDER BY h.hospital_name, bi.blood_group
        """
        return db.fetch_all(query)
    
    @staticmethod
    def update_units(inventory_id, units_available, units_reserved, updated_by):
        """Update inventory units"""
        query = """
            UPDATE BLOOD_INVENTORY
            SET units_available = %s, 
                units_reserved = %s,
                updated_by = %s,
                last_updated = NOW()
            WHERE inventory_id = %s
        """
        db.execute_query(query, (units_available, units_reserved, updated_by, inventory_id))