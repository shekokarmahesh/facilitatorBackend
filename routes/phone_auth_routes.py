from flask import Blueprint, jsonify, request, session
from models.database import DatabaseManager, FacilitatorRepository
import random
import re
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Initialize database components
db_manager = DatabaseManager()
facilitator_repo = FacilitatorRepository(db_manager)

def validate_phone_number(phone_number):
    """Validate phone number format"""
    # Basic validation for international format
    phone_pattern = r'^\+[1-9]\d{1,14}$'
    return re.match(phone_pattern, phone_number) is not None

def generate_otp():
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_sms(phone_number, message):
    """
    Send SMS via your SMS provider
    TODO: Implement with your chosen SMS service (Twilio, AWS SNS, etc.)
    """
    # For now, just log the OTP (replace with actual SMS service)
    print(f"SMS to {phone_number}: {message}")
    return True

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to phone number"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        # Validate input
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400
        
        if not validate_phone_number(phone_number):
            return jsonify({"error": "Invalid phone number format. Use international format (+1234567890)"}), 400
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in database
        otp_id = facilitator_repo.create_otp(phone_number, otp)
        
        if not otp_id:
            return jsonify({"error": "Failed to generate OTP. Please try again."}), 500
        
        # Send SMS
        sms_message = f"Your verification code is: {otp}. Valid for 10 minutes."
        if send_sms(phone_number, sms_message):
            return jsonify({
                "success": True,
                "message": "OTP sent successfully",
                "phone_number": phone_number
            }), 200
        else:
            return jsonify({"error": "Failed to send SMS. Please try again."}), 500
            
    except Exception as e:
        print(f"Error in send_otp: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and determine user flow"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        
        # Validate input
        if not phone_number or not otp:
            return jsonify({"error": "Phone number and OTP are required"}), 400
        
        if not validate_phone_number(phone_number):
            return jsonify({"error": "Invalid phone number format"}), 400
        
        if len(otp) != 6 or not otp.isdigit():
            return jsonify({"error": "OTP must be 6 digits"}), 400
        
        # Verify OTP and get user status
        result = facilitator_repo.verify_otp_and_get_user_status(phone_number, otp)
        
        if result["success"]:
            if result["is_new_user"]:
                # New user - set temporary session for onboarding
                session['temp_phone_number'] = phone_number
                session['otp_verified'] = True
                session['verification_timestamp'] = datetime.now().isoformat()
                
                return jsonify({
                    "success": True,
                    "is_new_user": True,
                    "redirect_to": "onboarding",
                    "message": "OTP verified. Please complete your profile."
                }), 200
            else:
                # Existing user - set full session
                facilitator = result["facilitator"]
                session['facilitator_id'] = facilitator['id']
                session['phone_number'] = phone_number
                session['is_authenticated'] = True
                session['login_timestamp'] = datetime.now().isoformat()
                
                return jsonify({
                    "success": True,
                    "is_new_user": False,
                    "redirect_to": "dashboard",
                    "facilitator": {
                        "id": facilitator['id'],
                        "phone_number": facilitator['phone_number'],
                        "name": facilitator['name'],
                        "email": facilitator['email']
                    },
                    "message": "Login successful"
                }), 200
        else:
            return jsonify({"error": result["message"]}), 400
            
    except Exception as e:
        print(f"Error in verify_otp: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/complete-onboarding', methods=['POST'])
def complete_onboarding():
    """Complete onboarding for new users"""
    try:
        # Verify session
        phone_number = session.get('temp_phone_number')
        otp_verified = session.get('otp_verified')
        
        if not phone_number or not otp_verified:
            return jsonify({"error": "Invalid session. Please verify OTP again."}), 401
        
        # Check if user already exists (security check)
        existing_facilitator = facilitator_repo.get_facilitator_by_phone(phone_number)
        if existing_facilitator:
            return jsonify({"error": "User already exists. Please login instead."}), 400
        
        # Get onboarding data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Prepare onboarding data
        onboarding_data = {
            "name": data.get('name'),
            "email": data.get('email'),
            "basic_info": data.get('basic_info'),
            "professional_details": data.get('professional_details'),
            "bio_about": data.get('bio_about'),
            "experience": data.get('experience'),
            "certifications": data.get('certifications'),
            "visual_profile": data.get('visual_profile')
        }
        
        # Create facilitator profile
        facilitator = facilitator_repo.complete_onboarding(phone_number, onboarding_data)
        
        if facilitator:
            # Clear temporary session
            session.pop('temp_phone_number', None)
            session.pop('otp_verified', None)
            session.pop('verification_timestamp', None)
            
            # Set authenticated session
            session['facilitator_id'] = facilitator['id']
            session['phone_number'] = phone_number
            session['is_authenticated'] = True
            session['login_timestamp'] = datetime.now().isoformat()
            
            return jsonify({
                "success": True,
                "message": "Onboarding completed successfully",
                "facilitator": {
                    "id": facilitator['id'],
                    "phone_number": facilitator['phone_number'],
                    "name": facilitator['name'],
                    "email": facilitator['email']
                },
                "redirect_to": "dashboard"
            }), 200
        else:
            return jsonify({"error": "Failed to complete onboarding. Please try again."}), 500
            
    except Exception as e:
        print(f"Error in complete_onboarding: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    try:
        # Clear all session data
        session.clear()
        
        return jsonify({
            "success": True,
            "message": "Logged out successfully"
        }), 200
        
    except Exception as e:
        print(f"Error in logout: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/session-status', methods=['GET'])
def session_status():
    """Check current session status"""
    try:
        is_authenticated = session.get('is_authenticated', False)
        facilitator_id = session.get('facilitator_id')
        phone_number = session.get('phone_number')
        temp_phone = session.get('temp_phone_number')
        otp_verified = session.get('otp_verified', False)
        
        if is_authenticated and facilitator_id:
            # Fully authenticated user
            return jsonify({
                "authenticated": True,
                "facilitator_id": facilitator_id,
                "phone_number": phone_number,
                "status": "authenticated"
            }), 200
        elif temp_phone and otp_verified:
            # User in onboarding process
            return jsonify({
                "authenticated": False,
                "temp_phone_number": temp_phone,
                "status": "onboarding_pending"
            }), 200
        else:
            # Not authenticated
            return jsonify({
                "authenticated": False,
                "status": "not_authenticated"
            }), 200
            
    except Exception as e:
        print(f"Error in session_status: {e}")
        return jsonify({"error": "Internal server error"}), 500

# CORS preflight handling
@auth_bp.route('/send-otp', methods=['OPTIONS'])
@auth_bp.route('/verify-otp', methods=['OPTIONS'])
@auth_bp.route('/complete-onboarding', methods=['OPTIONS'])
@auth_bp.route('/logout', methods=['OPTIONS'])
@auth_bp.route('/session-status', methods=['OPTIONS'])
def handle_options():
    """Handle CORS preflight requests"""
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response
