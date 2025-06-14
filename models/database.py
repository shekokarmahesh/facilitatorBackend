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
        
        # Setup tables
        self._setup_tables()
    
    def _setup_tables(self):
        """Setup tables in PostgreSQL"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS otps (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            otp INTEGER NOT NULL,
            password VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS facilitator_profiles (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(255) NOT NULL,
            user_id INTEGER NOT NULL,
            basic_info JSONB,
            professional_details JSONB,
            bio_about JSONB,
            experience JSONB,
            certifications JSONB,
            visual_profile JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS offerings (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(255) NOT NULL,
            user_id INTEGER NOT NULL,
            basic_info JSONB,
            details JSONB,
            price_schedule JSONB,
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

    def create_user(self, tenant_id: str, email: str, password: str):
        """Create a new user"""
        try:
            self.db_manager.cursor.execute(
                """
                INSERT INTO users (tenant_id, email, password, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id;
                """,
                (tenant_id, email, password, True)
            )
            user_id = self.db_manager.cursor.fetchone()[0]
            self.db_manager.connection.commit()
            return user_id
        except psycopg2.Error as e:
            print(f"Error creating user: {e}")
            return None

    def update_facilitator_profile(self, tenant_id: str, user_id: int, update_data: dict):
        """Update facilitator profile"""
        try:
            self.db_manager.cursor.execute(
                """
                UPDATE facilitator_profiles
                SET basic_info = %s, professional_details = %s, bio_about = %s,
                    experience = %s, certifications = %s, visual_profile = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE tenant_id = %s AND user_id = %s;
                """,
                (
                    update_data.get("basic_info"),
                    update_data.get("professional_details"),
                    update_data.get("bio_about"),
                    update_data.get("experience"),
                    update_data.get("certifications"),
                    update_data.get("visual_profile"),
                    tenant_id,
                    user_id
                )
            )
            self.db_manager.connection.commit()
        except psycopg2.Error as e:
            print(f"Error updating facilitator profile: {e}")

    def get_facilitator_profile(self, tenant_id: str, user_id: int):
        """Get complete facilitator profile"""
        try:
            self.db_manager.cursor.execute(
                """
                SELECT * FROM facilitator_profiles
                WHERE tenant_id = %s AND user_id = %s;
                """,
                (tenant_id, user_id)
            )
            profile = self.db_manager.cursor.fetchone()
            return dict(profile) if profile else None
        except psycopg2.Error as e:
            print(f"Error fetching facilitator profile: {e}")
            return None

    def get_facilitator_offerings(self, tenant_id: str, user_id: int):
        """Get all offerings for a facilitator"""
        try:
            self.db_manager.cursor.execute(
                """
                SELECT * FROM offerings
                WHERE tenant_id = %s AND user_id = %s;
                """,
                (tenant_id, user_id)
            )
            offerings = self.db_manager.cursor.fetchall()
            return [dict(offering) for offering in offerings]
        except psycopg2.Error as e:
            print(f"Error fetching facilitator offerings: {e}")
            return []

    def search_facilitators(self, tenant_id: str, filters: dict = None, page: int = 1, limit: int = 10):
        """Search facilitators with filters and pagination"""
        query = "SELECT * FROM facilitator_profiles WHERE tenant_id = %s"
        params = [tenant_id]

        if filters:
            for key, value in filters.items():
                query += f" AND {key} = %s"
                params.append(value)

        query += " LIMIT %s OFFSET %s"
        params.extend([limit, (page - 1) * limit])

        try:
            self.db_manager.cursor.execute(query, tuple(params))
            facilitators = self.db_manager.cursor.fetchall()
            return [dict(facilitator) for facilitator in facilitators]
        except psycopg2.Error as e:
            print(f"Error searching facilitators: {e}")
            return []

# Usage example
if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager._setup_tables()
    db_manager.close_connection()
