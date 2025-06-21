import os
import json
from models.database import DatabaseManager

# Initialize DatabaseManager
db_manager = DatabaseManager()

def clear_existing_data():
    """Clear all existing data from the database."""
    try:
        db_manager.cursor.execute("TRUNCATE TABLE phone_otps, offerings, facilitators RESTART IDENTITY CASCADE;")
        db_manager.connection.commit()
        print("All existing data cleared.")
    except Exception as e:
        print(f"Error clearing data: {e}")

def insert_dummy_data():
    """Insert one manually defined dummy row into each table."""
    try:
        # Insert into facilitators
        db_manager.cursor.execute(
            """
            INSERT INTO facilitators (phone_number, email, name, basic_info, professional_details, bio_about, experience, certifications, visual_profile)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                "+1234567890",  # phone_number
                "dummy.email@example.com",  # email
                "John Doe",  # name
                json.dumps({"age": 30, "location": "New York"}),  # basic_info
                json.dumps({"profession": "Engineer", "company": "TechCorp"}),  # professional_details
                json.dumps({"bio": "Experienced professional with a passion for teaching."}),  # bio_about
                json.dumps({"years": 10}),  # experience
                json.dumps({"certifications": ["Certified Trainer", "Project Manager"]}),  # certifications
                json.dumps({"profile_picture": "http://example.com/profile.jpg"})  # visual_profile
            )
        )

        # Insert into offerings
        db_manager.cursor.execute(
            """
            INSERT INTO offerings (facilitator_id, title, description, category, basic_info, details, price_schedule)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            (
                1,  # facilitator_id
                "Introduction to Python",  # title
                "A comprehensive beginner's course on Python programming.",  # description
                "Programming",  # category
                json.dumps({"duration": "5 hours"}),  # basic_info
                json.dumps({"details": "This course covers the basics of Python, including syntax, data types, and functions."}),  # details
                json.dumps({"price": 500})  # price_schedule
            )
        )

        # Insert into phone_otps
        db_manager.cursor.execute(
            """
            INSERT INTO phone_otps (phone_number, otp, created_at, expires_at)
            VALUES (%s, %s, %s, %s);
            """,
            (
                "+1234567890",  # phone_number
                "123456",  # otp
                "2025-06-21 10:00:00",  # created_at
                "2025-06-21 10:05:00"  # expires_at
            )
        )

        db_manager.connection.commit()
        print("Dummy data inserted successfully.")
    except Exception as e:
        print(f"Error inserting dummy data: {e}")

def main():
    # Drop and recreate tables to ensure schema is correct
    db_manager.cursor.execute("DROP TABLE IF EXISTS phone_otps, offerings, facilitators CASCADE;")
    db_manager._setup_tables()

    clear_existing_data()
    insert_dummy_data()
    db_manager.close_connection()

if __name__ == "__main__":
    main()
