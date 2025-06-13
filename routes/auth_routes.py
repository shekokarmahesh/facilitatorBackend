from flask import Blueprint, jsonify, request
from helpers.jwt_helper import generate_jwt
from middleware.token_required import token_required
from models.database import users_collection, otps_collection
from helpers.email_helper import send_email
import random

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    otp = random.randint(100000, 999999)
    otps_collection.insert_one({"email": email, "otp": otp, "password": password})

    send_email(email, f"Your OTP is {otp}")

    return jsonify({"message": "OTP sent to email"})

@auth_routes.route('/verify', methods=['POST'])
def verify():
    data = request.json
    email = data.get('email')
    otp = int(data.get('otp'))

    otp_record = otps_collection.find_one({"email": email, "otp": otp})
    if otp_record:
        users_collection.insert_one({"email": email, "password": otp_record.get('password')})
        otps_collection.delete_one({"email": email})
        token = generate_jwt(email)
        return jsonify({"message": "Email verified and registered successfully", "token": token})

    return jsonify({"error": "Invalid OTP"}), 400

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email, "password": password})
    if user:
        token = generate_jwt(email)
        return jsonify({"message": "Login successful", "token": token})

    return jsonify({"error": "Invalid email or password"}), 400

@auth_routes.route('/refresh-token', methods=['POST'])
@token_required
def refresh_token():
    new_token = generate_jwt(request.user_email)
    return jsonify({"message": "Token refreshed successfully", "token": new_token})
