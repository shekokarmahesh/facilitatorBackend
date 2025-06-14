import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timezone
from bcrypt import hashpw, gensalt
import os
from dotenv import load_dotenv
import json

load_dotenv()

# PostgreSQL connection setup
postgres_url = os.getenv("POSTGRES_URL")
connection = psycopg2.connect(postgres_url)
cursor = connection.cursor()

# Sample data
users_data = [
    {
        "tenant_id": "675b1234567890abcdef1234",
        "email": "john@example.com",
        "password": hashpw("password123".encode('utf-8'), gensalt()).decode('utf-8'),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "tenant_id": "675b1234567890abcdef1234",
        "email": "jane@example.com",
        "password": hashpw("securepass".encode('utf-8'), gensalt()).decode('utf-8'),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
]

facilitator_profiles_data = [
    {
        "tenant_id": "675b1234567890abcdef1234",
        "user_id": "64b1234567890abcdef1234",
        "basic_info": {
            "first_name": "John",
            "last_name": "Doe",
            "phone_no": "+1234567890",
            "location": "New York"
        },
        "professional_details": {
            "languages": ["English", "Spanish"],
            "teaching_styles": ["Interactive", "Hands-on"],
            "specializations": ["Web Development", "Data Science"]
        },
        "bio_about": {
            "short_bio": "Experienced web developer and data scientist.",
            "detailed_about": "John has over 10 years of experience in web development and data science. He specializes in creating interactive learning experiences."
        },
        "experience": [
            {
                "title": "Senior Developer",
                "organization_name": "TechCorp",
                "date_started": datetime(2015, 1, 1, tzinfo=timezone.utc),
                "date_ended": datetime(2020, 12, 31, tzinfo=timezone.utc)
            },
            {
                "title": "Data Scientist",
                "organization_name": "DataWorks",
                "date_started": datetime(2021, 1, 1, tzinfo=timezone.utc),
                "date_ended": None
            }
        ],
        "certifications": [
            {
                "title": "Certified Web Developer",
                "organization_name": "WebCert",
                "date_started": datetime(2016, 1, 1, tzinfo=timezone.utc),
                "date_ended": datetime(2016, 12, 31, tzinfo=timezone.utc),
                "image_url": "https://example.com/certification1.jpg"
            }
        ],
        "visual_profile": {
            "banner_image_url": "https://example.com/banner.jpg",
            "intro_video_url": "https://example.com/intro.mp4",
            "profile_pic_url": "https://example.com/profile.jpg",
            "gallery_images": [
                "https://example.com/gallery1.jpg",
                "https://example.com/gallery2.jpg"
            ]
        }
    }
]

offerings_data = [
    {
        "tenant_id": "675b1234567890abcdef1234",
        "user_id": "64b1234567890abcdef1234",
        "basic_info": {
            "title": "Web Development Bootcamp",
            "description": "Learn web development from scratch in this interactive bootcamp.",
            "offering_tags": ["Web Development", "Bootcamp"],
            "categories": ["Programming", "Technology"]
        },
        "details": {
            "required_materials": "Laptop, Internet connection",
            "pre_requisites": "Basic knowledge of programming"
        },
        "price_schedule": {
            "price": 499.99,
            "duration": "4 weeks",
            "max_participants": 20,
            "location": "Online"
        }
    },
    {
        "tenant_id": "675b1234567890abcdef1234",
        "user_id": "64b1234567890abcdef5678",
        "basic_info": {
            "title": "Data Science Workshop",
            "description": "An advanced workshop on data science techniques and tools.",
            "offering_tags": ["Data Science", "Workshop"],
            "categories": ["Technology", "Analytics"]
        },
        "details": {
            "required_materials": "Laptop, Python installed",
            "pre_requisites": "Basic knowledge of statistics"
        },
        "price_schedule": {
            "price": 299.99,
            "duration": "2 weeks",
            "max_participants": 15,
            "location": "Online"
        }
    }
]


# Ensure tables exist
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        tenant_id VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        is_active BOOLEAN NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    );

    CREATE TABLE IF NOT EXISTS facilitator_profiles (
        id SERIAL PRIMARY KEY,
        tenant_id VARCHAR(255) NOT NULL,
        user_id VARCHAR(255) NOT NULL,
        basic_info JSONB NOT NULL,
        professional_details JSONB NOT NULL,
        bio_about JSONB NOT NULL,
        experience JSONB NOT NULL,
        certifications JSONB NOT NULL,
        visual_profile JSONB NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    );

    CREATE TABLE IF NOT EXISTS offerings (
        id SERIAL PRIMARY KEY,
        tenant_id VARCHAR(255) NOT NULL,
        user_id VARCHAR(255) NOT NULL,
        basic_info JSONB NOT NULL,
        details JSONB NOT NULL,
        price_schedule JSONB NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    );
    """)
    connection.commit()
    print("Tables created successfully.")
except psycopg2.Error as e:
    print(f"Error creating tables: {e}")

# Clear database
try:
    cursor.execute("DELETE FROM users;")
    cursor.execute("DELETE FROM facilitator_profiles;")
    cursor.execute("DELETE FROM offerings;")
    connection.commit()
    print("Database cleared successfully.")
except psycopg2.Error as e:
    print(f"Error clearing database: {e}")

# Convert datetime objects to ISO format strings
for profile in facilitator_profiles_data:
    profile["experience"] = [
        {
            **exp,
            "date_started": exp["date_started"].isoformat() if exp["date_started"] else None,
            "date_ended": exp["date_ended"].isoformat() if exp["date_ended"] else None
        }
        for exp in profile["experience"]
    ]
    profile["certifications"] = [
        {
            **cert,
            "date_started": cert["date_started"].isoformat() if cert["date_started"] else None,
            "date_ended": cert["date_ended"].isoformat() if cert["date_ended"] else None
        }
        for cert in profile["certifications"]
    ]

for offering in offerings_data:
    offering["price_schedule"] = {
        **offering["price_schedule"],
        "price": float(offering["price_schedule"]["price"]),
    }

# Populate users data
try:
    execute_values(
        cursor,
        """
        INSERT INTO users (tenant_id, email, password, is_active, created_at, updated_at)
        VALUES %s;
        """,
        [(user["tenant_id"], user["email"], user["password"], user["is_active"], user["created_at"], user["updated_at"]) for user in users_data]
    )
    connection.commit()
    print("Users data inserted successfully.")
except psycopg2.Error as e:
    print(f"Error populating users: {e}")

# Populate facilitator profiles data
try:
    execute_values(
        cursor,
        """
        INSERT INTO facilitator_profiles (tenant_id, user_id, basic_info, professional_details, bio_about, experience, certifications, visual_profile, created_at, updated_at)
        VALUES %s;
        """,
        [(
            profile["tenant_id"],
            profile["user_id"],
            json.dumps(profile["basic_info"]),
            json.dumps(profile["professional_details"]),
            json.dumps(profile["bio_about"]),
            json.dumps(profile["experience"]),
            json.dumps(profile["certifications"]),
            json.dumps(profile["visual_profile"]),
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ) for profile in facilitator_profiles_data]
    )
    connection.commit()
    print("Facilitator profiles data inserted successfully.")
except psycopg2.Error as e:
    print(f"Error populating facilitator profiles: {e}")

# Populate offerings data
try:
    execute_values(
        cursor,
        """
        INSERT INTO offerings (tenant_id, user_id, basic_info, details, price_schedule, created_at, updated_at)
        VALUES %s;
        """,
        [(
            offering["tenant_id"],
            offering["user_id"],
            json.dumps(offering["basic_info"]),
            json.dumps(offering["details"]),
            json.dumps(offering["price_schedule"]),
            datetime.now(timezone.utc),
            datetime.now(timezone.utc)
        ) for offering in offerings_data]
    )
    connection.commit()
    print("Offerings data inserted successfully.")
except psycopg2.Error as e:
    print(f"Error populating offerings: {e}")

# Close connection
cursor.close()
connection.close()
