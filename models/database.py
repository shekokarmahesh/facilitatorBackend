import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    def __init__(self):
        # PostgreSQL setup
        self.postgres_url = os.getenv("POSTGRES_URL")
        self.connection = psycopg2.connect(self.postgres_url, cursor_factory=DictCursor)
        self.cursor = self.connection.cursor()
        # Setup tables        self._setup_tables()
    
    def _setup_tables(self):
        """Setup tables in PostgreSQL"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS facilitators (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(20) UNIQUE NOT NULL,
            email VARCHAR(255),
            name VARCHAR(255),
            basic_info JSONB,
            professional_details JSONB,
            bio_about JSONB,
            experience JSONB,
            certifications JSONB,
            visual_profile JSONB,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );        CREATE TABLE IF NOT EXISTS phone_otps (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(20) NOT NULL,
            otp VARCHAR(6) NOT NULL,
            otp_type VARCHAR(20) NOT NULL DEFAULT 'verification', -- 'verification' for unified flow
            expires_at TIMESTAMP NOT NULL,
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS offerings (
            id SERIAL PRIMARY KEY,
            facilitator_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(100),
            basic_info JSONB,
            details JSONB,
            price_schedule JSONB,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

# Repository pattern for cleaner data access
class FacilitatorRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create_facilitator(self, phone_number: str, email: str = None, name: str = None):
        """Create a new facilitator"""
        try:
            self.db_manager.cursor.execute(
                """
                INSERT INTO facilitators (phone_number, email, name, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id;
                """,
                (phone_number, email, name, True)
            )
            facilitator_id = self.db_manager.cursor.fetchone()[0]
            self.db_manager.connection.commit()
            return facilitator_id
        except psycopg2.Error as e:
            print(f"Error creating facilitator: {e}")
            return None

    def update_facilitator_profile(self, facilitator_id: int, update_data: dict):
        """Update facilitator profile"""
        try:
            self.db_manager.cursor.execute(
                """
                UPDATE facilitators
                SET basic_info = %s, professional_details = %s, bio_about = %s,
                    experience = %s, certifications = %s, visual_profile = %s,
                    email = %s, name = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (
                    update_data.get("basic_info"),
                    update_data.get("professional_details"),
                    update_data.get("bio_about"),
                    update_data.get("experience"),
                    update_data.get("certifications"),
                    update_data.get("visual_profile"),
                    update_data.get("email"),
                    update_data.get("name"),
                    facilitator_id
                )
            )
            self.db_manager.connection.commit()
        except psycopg2.Error as e:
            print(f"Error updating facilitator profile: {e}")

    def get_facilitator_profile(self, facilitator_id: int):
        """Get complete facilitator profile"""
        try:
            self.db_manager.cursor.execute(
                """
                SELECT * FROM facilitators
                WHERE id = %s;
                """,
                (facilitator_id,)
            )
            profile = self.db_manager.cursor.fetchone()
            return dict(profile) if profile else None
        except psycopg2.Error as e:
            print(f"Error fetching facilitator profile: {e}")
            return None

    def create_offering(self, facilitator_id: int, offering_data: dict):
        """Create a new offering for a facilitator"""
        try:
            self.db_manager.cursor.execute(
                """
                INSERT INTO offerings (facilitator_id, title, description, category, 
                                     basic_info, details, price_schedule, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id;
                """,
                (
                    facilitator_id,
                    offering_data.get("title"),
                    offering_data.get("description"),
                    offering_data.get("category"),
                    offering_data.get("basic_info"),
                    offering_data.get("details"),
                    offering_data.get("price_schedule"),
                    True
                )
            )
            offering_id = self.db_manager.cursor.fetchone()[0]
            self.db_manager.connection.commit()
            return offering_id
        except psycopg2.Error as e:
            print(f"Error creating offering: {e}")
            return None

    def update_offering(self, offering_id: int, update_data: dict):
        """Update an offering"""
        try:
            self.db_manager.cursor.execute(
                """
                UPDATE offerings
                SET title = %s, description = %s, category = %s,
                    basic_info = %s, details = %s, price_schedule = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (
                    update_data.get("title"),
                    update_data.get("description"),
                    update_data.get("category"),
                    update_data.get("basic_info"),
                    update_data.get("details"),
                    update_data.get("price_schedule"),
                    offering_id
                )
            )
            self.db_manager.connection.commit()
        except psycopg2.Error as e:
            print(f"Error updating offering: {e}")

    def delete_offering(self, offering_id: int):
        """Soft delete an offering by setting is_active to False"""
        try:
            self.db_manager.cursor.execute(
                """
                UPDATE offerings
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (offering_id,)
            )
            self.db_manager.connection.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error deleting offering: {e}")
            return False

    def get_facilitator_offerings(self, facilitator_id: int):
        """Get all offerings for a facilitator"""
        try:
            self.db_manager.cursor.execute(
                """
                SELECT * FROM offerings
                WHERE facilitator_id = %s AND is_active = TRUE;
                """,
                (facilitator_id,)
            )
            offerings = self.db_manager.cursor.fetchall()
            return [dict(offering) for offering in offerings]
        except psycopg2.Error as e:
            print(f"Error fetching facilitator offerings: {e}")
            return []

    def search_facilitators(self, filters: dict = None, page: int = 1, limit: int = 10):
        """Search facilitators with filters and pagination"""
        query = "SELECT * FROM facilitators WHERE is_active = TRUE"
        params = []

        if filters:
            for key, value in filters.items():
                if key in ['name', 'email']:  # Only allow safe columns for direct filtering
                    query += f" AND {key} ILIKE %s"
                    params.append(f"%{value}%")

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, (page - 1) * limit])

        try:
            self.db_manager.cursor.execute(query, tuple(params))
            facilitators = self.db_manager.cursor.fetchall()
            return [dict(facilitator) for facilitator in facilitators]
        except psycopg2.Error as e:
            print(f"Error searching facilitators: {e}")
            return []

    def search_offerings(self, filters: dict = None, page: int = 1, limit: int = 10):
        """Search offerings with filters and pagination"""
        query = "SELECT * FROM offerings WHERE is_active = TRUE"
        params = []

        if filters:
            for key, value in filters.items():
                if key in ['title', 'description', 'category']:  # Only allow safe columns
                    query += f" AND {key} ILIKE %s"
                    params.append(f"%{value}%")

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, (page - 1) * limit])

        try:
            self.db_manager.cursor.execute(query, tuple(params))
            offerings = self.db_manager.cursor.fetchall()
            return [dict(offering) for offering in offerings]
        except psycopg2.Error as e:
            print(f"Error searching offerings: {e}")
            return []

    def get_facilitator_by_phone(self, phone_number: str):
        """Get facilitator by phone number for authentication"""
        try:
            self.db_manager.cursor.execute(
                """
                SELECT * FROM facilitators
                WHERE phone_number = %s AND is_active = TRUE;
                """,
                (phone_number,)
            )
            facilitator = self.db_manager.cursor.fetchone()
            return dict(facilitator) if facilitator else None
        except psycopg2.Error as e:
            print(f"Error fetching facilitator by phone: {e}")
            return None

    def create_otp(self, phone_number: str, otp: str, expires_in_minutes: int = 10):
        """Create OTP for phone verification (unified for all users)"""
        try:
            self.db_manager.cursor.execute(
                """
                INSERT INTO phone_otps (phone_number, otp, otp_type, expires_at, is_verified, created_at)
                VALUES (%s, %s, %s, NOW() + INTERVAL '%s minutes', FALSE, CURRENT_TIMESTAMP)
                RETURNING id;
                """,
                (phone_number, otp, 'verification', expires_in_minutes)
            )
            otp_id = self.db_manager.cursor.fetchone()[0]
            self.db_manager.connection.commit()
            return otp_id
        except psycopg2.Error as e:
            print(f"Error creating OTP: {e}")
            return None

    def verify_otp_and_get_user_status(self, phone_number: str, otp: str):
        """Verify OTP and return user status (new/existing)"""
        try:
            # First verify the OTP
            self.db_manager.cursor.execute(
                """
                SELECT id FROM phone_otps
                WHERE phone_number = %s AND otp = %s AND otp_type = 'verification'
                AND expires_at > NOW() AND is_verified = FALSE
                ORDER BY created_at DESC
                LIMIT 1;
                """,
                (phone_number, otp)
            )
            
            otp_record = self.db_manager.cursor.fetchone()
            
            if not otp_record:
                return {"success": False, "message": "Invalid or expired OTP"}
            
            # Mark OTP as verified
            self.db_manager.cursor.execute(
                """
                UPDATE phone_otps
                SET is_verified = TRUE
                WHERE id = %s;
                """,
                (otp_record['id'],)
            )
            self.db_manager.connection.commit()
            
            # Check if facilitator already exists
            existing_facilitator = self.get_facilitator_by_phone(phone_number)
            
            if existing_facilitator:
                # Existing user - redirect to dashboard
                return {
                    "success": True,
                    "is_new_user": False,
                    "facilitator": existing_facilitator,
                    "phone_number": phone_number,
                    "redirect_to": "dashboard"
                }
            else:
                # New user - redirect to onboarding (NO profile creation yet)
                return {
                    "success": True,
                    "is_new_user": True,
                    "facilitator": None,
                    "phone_number": phone_number,
                    "redirect_to": "onboarding"
                }
                
        except psycopg2.Error as e:
            print(f"Error verifying OTP and checking user status: {e}")
            return {"success": False, "message": "Database error"}

    def verify_otp(self, phone_number: str, otp: str, otp_type: str = 'verification'):
        """Simple OTP verification (for backward compatibility)"""
        try:
            self.db_manager.cursor.execute(
                """
                SELECT id FROM phone_otps
                WHERE phone_number = %s AND otp = %s AND otp_type = %s
                AND expires_at > NOW() AND is_verified = FALSE
                ORDER BY created_at DESC
                LIMIT 1;
                """,
                (phone_number, otp, otp_type)
            )
            
            otp_record = self.db_manager.cursor.fetchone()
            
            if otp_record:
                self.db_manager.cursor.execute(
                    """
                    UPDATE phone_otps
                    SET is_verified = TRUE
                    WHERE id = %s;
                    """,
                    (otp_record['id'],)
                )
                self.db_manager.connection.commit()
                return True
            return False
            
        except psycopg2.Error as e:
            print(f"Error verifying OTP: {e}")
            return False

    def cleanup_expired_otps(self):
        """Remove expired OTP records"""
        try:
            self.db_manager.cursor.execute(
                """
                DELETE FROM phone_otps
                WHERE expires_at < NOW();
                """
            )
            deleted_count = self.db_manager.cursor.rowcount
            self.db_manager.connection.commit()
            return deleted_count
        except psycopg2.Error as e:
            print(f"Error cleaning up expired OTPs: {e}")
            return 0

    def verify_offering_ownership(self, facilitator_id: int, offering_id: int):
        """Verify that the offering belongs to the facilitator"""
        try:
            self.db_manager.cursor.execute(
                """
                SELECT 1 FROM offerings
                WHERE id = %s AND facilitator_id = %s;
                """,
                (offering_id, facilitator_id)
            )
            return self.db_manager.cursor.fetchone() is not None
        except psycopg2.Error as e:
            print(f"Error verifying offering ownership: {e}")
            return False

    def complete_onboarding(self, phone_number: str, onboarding_data: dict):
        """Create facilitator profile after onboarding completion"""
        try:
            # Create facilitator with onboarding data
            self.db_manager.cursor.execute(
                """
                INSERT INTO facilitators (phone_number, email, name, basic_info, 
                                        professional_details, bio_about, experience, 
                                        certifications, visual_profile, is_active, 
                                        created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id;
                """,
                (
                    phone_number,
                    onboarding_data.get("email"),
                    onboarding_data.get("name"),
                    onboarding_data.get("basic_info"),
                    onboarding_data.get("professional_details"),
                    onboarding_data.get("bio_about"),
                    onboarding_data.get("experience"),
                    onboarding_data.get("certifications"),
                    onboarding_data.get("visual_profile"),
                    True
                )
            )
            facilitator_id = self.db_manager.cursor.fetchone()[0]
            self.db_manager.connection.commit()
            
            # Return the newly created facilitator profile
            return self.get_facilitator_profile(facilitator_id)
            
        except psycopg2.Error as e:
            print(f"Error completing onboarding: {e}")
            return None

# Usage example
if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager._setup_tables()
    db_manager.close_connection()
