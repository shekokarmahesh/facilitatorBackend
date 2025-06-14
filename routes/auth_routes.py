from flask import Blueprint, jsonify, request
from helpers.jwt_helper import generate_jwt
from middleware.token_required import token_required
from models.database import DatabaseManager
from helpers.email_helper import send_email
import random
import uuid

auth_routes = Blueprint('auth_routes', __name__)

db_manager = DatabaseManager()

@auth_routes.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_routes.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and complete registration"""
    try:
        data = request.json
        email = data.get('email')
        otp = int(data.get('otp'))

        if not email or not otp:
            return jsonify({"error": "Email and OTP are required"}), 400

        db_manager.cursor.execute("SELECT * FROM otps WHERE email = %s AND otp = %s", (email, otp))
        otp_record = db_manager.cursor.fetchone()
        
        if otp_record:
            # Generate tenant_id for new user
            tenant_id = str(uuid.uuid4())
            
            db_manager.cursor.execute(
                "INSERT INTO users (tenant_id, email, password, is_active, created_at, updated_at) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                (tenant_id, email, otp_record['password'], True)
            )
            db_manager.cursor.execute("DELETE FROM otps WHERE email = %s", (email,))
            db_manager.connection.commit()

            token = generate_jwt(email)
            
            # Get user info for response
            db_manager.cursor.execute("SELECT id, email, tenant_id, is_active FROM users WHERE email = %s", (email,))
            user = db_manager.cursor.fetchone()
            
            return jsonify({
                "message": "Email verified and registered successfully",
                "token": token,
                "user": {
                    "id": str(user['id']),
                    "email": user['email'],
                    "tenant_id": user['tenant_id'],
                    "is_active": user['is_active']
                }
            })

        return jsonify({"error": "Invalid OTP"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_routes.route('/api/auth/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP"""
    try:
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Check if there's a pending OTP
        db_manager.cursor.execute("SELECT * FROM otps WHERE email = %s", (email,))
        existing_otp = db_manager.cursor.fetchone()
        
        if not existing_otp:
            return jsonify({"error": "No pending registration found for this email"}), 400

        # Generate new OTP
        otp = random.randint(100000, 999999)
        db_manager.cursor.execute(
            "UPDATE otps SET otp = %s, created_at = CURRENT_TIMESTAMP WHERE email = %s",
            (otp, email)
        )
        db_manager.connection.commit()

        send_email(email, f"Your new OTP is {otp}")

        return jsonify({"message": "New OTP sent to email"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_routes.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        db_manager.cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = db_manager.cursor.fetchone()
        
        if user:
            token = generate_jwt(email)
            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": str(user['id']),
                    "email": user['email'],
                    "tenant_id": user['tenant_id'],
                    "is_active": user['is_active']
                }
            })

        return jsonify({"error": "Invalid email or password"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_routes.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({"message": "Logged out successfully"})

@auth_routes.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user info"""
    try:
        user_email = request.user_email
        
        db_manager.cursor.execute("SELECT id, email, tenant_id, is_active FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": {
                "id": str(user['id']),
                "email": user['email'],
                "tenant_id": user['tenant_id'],
                "is_active": user['is_active']
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_routes.route('/api/auth/profile', methods=['PUT'])
@token_required
def update_user_profile():
    """Update user profile (email, password)"""
    try:
        data = request.json
        user_email = request.user_email
        
        # Get current user
        db_manager.cursor.execute("SELECT id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        
        # Update fields if provided
        if 'email' in data:
            new_email = data['email']
            # Check if new email is already taken
            db_manager.cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (new_email, user_id))
            if db_manager.cursor.fetchone():
                return jsonify({"error": "Email already in use"}), 400
            
            db_manager.cursor.execute(
                "UPDATE users SET email = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (new_email, user_id)
            )
        
        if 'password' in data:
            new_password = data['password']
            db_manager.cursor.execute(
                "UPDATE users SET password = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (new_password, user_id)
            )
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Profile updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_routes.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset OTP"""
    try:
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Check if user exists
        db_manager.cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if not db_manager.cursor.fetchone():
            return jsonify({"error": "Email not found"}), 404

        # Generate OTP for password reset
        otp = random.randint(100000, 999999)
        
        # Store or update OTP (reusing otps table)
        db_manager.cursor.execute("DELETE FROM otps WHERE email = %s", (email,))
        db_manager.cursor.execute(
            "INSERT INTO otps (email, otp, password, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)",
            (email, otp, 'password_reset')  # Use placeholder for password field
        )
        db_manager.connection.commit()

        send_email(email, f"Your password reset OTP is {otp}")

        return jsonify({"message": "Password reset OTP sent to email"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_routes.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password with OTP"""
    try:
        data = request.json
        email = data.get('email')
        otp = int(data.get('otp'))
        new_password = data.get('new_password')

        if not email or not otp or not new_password:
            return jsonify({"error": "Email, OTP, and new password are required"}), 400

        # Verify OTP
        db_manager.cursor.execute("SELECT * FROM otps WHERE email = %s AND otp = %s", (email, otp))
        otp_record = db_manager.cursor.fetchone()
        
        if not otp_record:
            return jsonify({"error": "Invalid OTP"}), 400

        # Update password
        db_manager.cursor.execute(
            "UPDATE users SET password = %s, updated_at = CURRENT_TIMESTAMP WHERE email = %s",
            (new_password, email)
        )
        
        # Delete OTP
        db_manager.cursor.execute("DELETE FROM otps WHERE email = %s", (email,))
        db_manager.connection.commit()

        return jsonify({"message": "Password reset successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_routes.route('/api/auth/refresh-token', methods=['POST'])
@token_required
def refresh_token():
    """Refresh JWT token"""
    try:
        new_token = generate_jwt(request.user_email)
        return jsonify({
            "message": "Token refreshed successfully",
            "token": new_token
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
