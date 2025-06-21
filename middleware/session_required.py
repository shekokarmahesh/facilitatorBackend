from functools import wraps
from flask import session, jsonify, request

def session_required(f):
    """
    Decorator to require valid session authentication
    Replaces the old token-based authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        is_authenticated = session.get('is_authenticated', False)
        facilitator_id = session.get('facilitator_id')
        
        if not is_authenticated or not facilitator_id:
            return jsonify({
                "error": "Authentication required",
                "message": "Please login to access this resource"
            }), 401
        
        # Add facilitator_id to request for easy access in routes
        request.facilitator_id = facilitator_id
        request.phone_number = session.get('phone_number')
        
        return f(*args, **kwargs)
    
    return decorated_function

def onboarding_session_required(f):
    """
    Decorator to require valid onboarding session
    Used for routes that should only be accessible during onboarding
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is in onboarding process
        temp_phone_number = session.get('temp_phone_number')
        otp_verified = session.get('otp_verified', False)
        
        if not temp_phone_number or not otp_verified:
            return jsonify({
                "error": "Invalid session",
                "message": "Please verify OTP first"
            }), 401
        
        # Check if user is already fully authenticated (shouldn't be in onboarding)
        if session.get('is_authenticated', False):
            return jsonify({
                "error": "Already authenticated",
                "message": "User is already registered"
            }), 400
        
        # Add temp phone number to request
        request.temp_phone_number = temp_phone_number
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_session(f):
    """
    Decorator that provides session info if available but doesn't require it
    Useful for public endpoints that can benefit from user context
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add session info to request if available
        request.facilitator_id = session.get('facilitator_id')
        request.phone_number = session.get('phone_number')
        request.is_authenticated = session.get('is_authenticated', False)
        
        return f(*args, **kwargs)
    
    return decorated_function
