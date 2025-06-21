import { auth, RecaptchaVerifier, signInWithPhoneNumber } from './firebase-config.js';

class PhoneAuth {
  constructor() {
    this.confirmationResult = null;
    this.recaptchaVerifier = null;
  }

  // Initialize reCAPTCHA
  setupRecaptcha(containerId = 'recaptcha-container') {
    if (!this.recaptchaVerifier) {
      this.recaptchaVerifier = new RecaptchaVerifier(containerId, {
        'size': 'invisible',
        'callback': (response) => {
          console.log('reCAPTCHA solved');
        },
        'expired-callback': () => {
          console.log('reCAPTCHA expired');
        }
      }, auth);
    }
    return this.recaptchaVerifier;
  }

  // Send OTP to phone number
  async sendOTP(phoneNumber) {
    try {
      // Setup reCAPTCHA if not already done
      const appVerifier = this.setupRecaptcha();
      
      console.log(`🔥 Sending OTP to ${phoneNumber}...`);
      
      // Send OTP via Firebase
      this.confirmationResult = await signInWithPhoneNumber(auth, phoneNumber, appVerifier);
      
      console.log('✅ OTP sent successfully!');
      return {
        success: true,
        message: 'OTP sent to your phone',
        verificationId: this.confirmationResult.verificationId
      };
      
    } catch (error) {
      console.error('❌ Error sending OTP:', error);
      
      // Reset reCAPTCHA on error
      if (this.recaptchaVerifier) {
        this.recaptchaVerifier.clear();
        this.recaptchaVerifier = null;
      }
      
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Verify OTP
  async verifyOTP(otp) {
    try {
      if (!this.confirmationResult) {
        throw new Error('Please send OTP first');
      }

      console.log(`🔍 Verifying OTP: ${otp}...`);
      
      // Verify OTP with Firebase
      const result = await this.confirmationResult.confirm(otp);
      const user = result.user;
      
      console.log('✅ OTP verified successfully!');
      console.log('Firebase User:', user);
      
      // Now call your backend with Firebase user data
      const backendResponse = await this.callBackendAuth(user);
      
      return {
        success: true,
        firebase_user: user,
        backend_response: backendResponse
      };
      
    } catch (error) {
      console.error('❌ Error verifying OTP:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Call your backend with Firebase user data
  async callBackendAuth(firebaseUser) {
    try {
      const response = await fetch('http://localhost:5000/api/auth/firebase-verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important for session cookies
        body: JSON.stringify({
          firebase_uid: firebaseUser.uid,
          phone_number: firebaseUser.phoneNumber
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Backend response:', data);
      
      return data;
    } catch (error) {
      console.error('Backend call failed:', error);
      throw error;
    }
  }

  // Complete onboarding for new users
  async completeOnboarding(userData) {
    try {
      const response = await fetch('http://localhost:5000/api/auth/complete-onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Onboarding failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const phoneAuth = new PhoneAuth();
