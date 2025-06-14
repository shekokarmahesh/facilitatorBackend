from flask import Blueprint, jsonify, request
from helpers.jwt_helper import generate_jwt
from middleware.token_required import token_required
from models.database import DatabaseManager
from helpers.email_helper import send_email
import random

auth_routes = Blueprint('auth_routes', __name__)

db_manager = DatabaseManager()

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    db_manager.cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
    if db_manager.cursor.fetchone():
        return jsonify({"error": "Email already registered"}), 400

    otp = random.randint(100000, 999999)
    db_manager.cursor.execute(
        "INSERT INTO otps (email, otp, password, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)",
        (email, otp, password)
    )
    db_manager.connection.commit()

    send_email(email, f"Your OTP is {otp}")

    return jsonify({"message": "OTP sent to email"})

@auth_routes.route('/verify', methods=['POST'])
def verify():
    data = request.json
    email = data.get('email')
    otp = int(data.get('otp'))

    db_manager.cursor.execute("SELECT * FROM otps WHERE email = %s AND otp = %s", (email, otp))
    otp_record = db_manager.cursor.fetchone()
    if otp_record:
        db_manager.cursor.execute(
            "INSERT INTO users (email, password, created_at, updated_at) VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
            (email, otp_record['password'])
        )
        db_manager.cursor.execute("DELETE FROM otps WHERE email = %s", (email,))
        db_manager.connection.commit()

        token = generate_jwt(email)
        return jsonify({"message": "Email verified and registered successfully", "token": token})

    return jsonify({"error": "Invalid OTP"}), 400

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    db_manager.cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = db_manager.cursor.fetchone()
    if user:
        token = generate_jwt(email)
        return jsonify({"message": "Login successful", "token": token})

    return jsonify({"error": "Invalid email or password"}), 400

@auth_routes.route('/refresh-token', methods=['POST'])
@token_required
def refresh_token():
    new_token = generate_jwt(request.user_email)
    return jsonify({"message": "Token refreshed successfully", "token": new_token})
