import os
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class FirebaseSMSService:
    def __init__(self):
        self.development_mode = os.getenv('DEVELOPMENT_MODE', 'True').lower() == 'true'
        self.project_id = os.getenv('FIREBASE_PROJECT_ID')
        self.credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        self.app = None
        
        # Initialize Firebase only if credentials are provided
        if self.credentials_path and os.path.exists(self.credentials_path):
            try:
                # Check if app is already initialized
                try:
                    self.app = firebase_admin.get_app()
                    print("Firebase app already initialized")
                except ValueError:
                    # App not initialized, create new one
                    cred = credentials.Certificate(self.credentials_path)
                    self.app = firebase_admin.initialize_app(cred, {
                        'projectId': self.project_id
                    })
                    print("✅ Firebase initialized successfully")
                    
            except Exception as e:
                print(f"❌ Firebase initialization failed: {e}")
                print("Falling back to development mode")
                self.development_mode = True
        else:
            print("⚠️ Firebase credentials not found - using development mode")
            self.development_mode = True
    
    def send_otp_sms(self, phone_number, otp):
        """
        Send OTP via Firebase Auth or print to console in development mode
        """
        try:
            message = f"Your AhoumCRM verification code is: {otp}. Valid for 10 minutes. Do not share this code."
            
            if self.development_mode:
                # Development mode - just print the OTP
                print(f"🔥 Firebase SMS (DEV MODE) to {phone_number}: {message}")
                print(f"📱 Use OTP: {otp} for testing")
                return True
            else:
                # Production mode - For now, we'll use a webhook or third-party SMS service
                # Firebase Auth doesn't directly send SMS - it requires client-side integration
                print(f"🔥 Firebase SMS (PROD MODE) - Would send to {phone_number}: {otp}")
                
                # Here you could integrate with:
                # 1. Twilio
                # 2. AWS SNS
                # 3. Firebase Functions with SMS provider
                # 4. Any SMS gateway API
                
                return self._send_production_sms(phone_number, otp)
                
        except Exception as e:
            print(f"❌ Error sending Firebase SMS: {e}")
            return False
    
    def _send_production_sms(self, phone_number, otp):
        """
        Send SMS in production mode using external SMS service
        This is where you'd integrate with your SMS provider
        """
        try:
            # For now, simulate production SMS sending
            print(f"📤 PRODUCTION SMS: Sending OTP {otp} to {phone_number}")
            print(f"📞 SMS Provider: Would call external SMS API here")
            
            # Example integration points:
            # - Twilio API call
            # - AWS SNS publish
            # - Firebase Cloud Functions
            # - Custom SMS gateway
            
            return True
            
        except Exception as e:
            print(f"❌ Production SMS failed: {e}")
            return False
    
    def verify_phone_with_firebase(self, phone_number):
        """
        Initiate phone verification with Firebase Auth
        """
        try:
            if self.development_mode:
                print(f"🔥 Firebase Phone Verification (DEV MODE) for {phone_number}")
                return {"success": True, "verification_id": "dev_verification_id"}
            else:
                print(f"🔥 Firebase Phone Verification (PROD MODE) for {phone_number}")
                # In production, you might use Firebase Auth REST API
                return {"success": True, "verification_id": "firebase_verification_id"}
                
        except Exception as e:
            print(f"❌ Error in Firebase phone verification: {e}")
            return {"success": False, "error": str(e)}

# Create a singleton instance
firebase_sms_service = FirebaseSMSService()
