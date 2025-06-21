from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routes.phone_auth_routes import auth_bp
from routes.facilitator_routes import facilitator_bp
from routes.offerings_routes import offerings_bp

app = Flask(__name__)

# Session configuration
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.permanent_session_lifetime = timedelta(days=7)  # Sessions last 7 days

# Enable CORS for all origins with credentials support
CORS(app, 
     resources={r"/*": {"origins": ["https://preview--ahoum-crm.lovable.app", "http://localhost:8080", "http://127.0.0.1:8080"]}},
     supports_credentials=True)

# Health check endpoint
@app.route('/ping', methods=['GET'])
def ping():
    """Simple health check endpoint"""
    return jsonify({
        "status": "success",
        "message": "Server is running",
        "timestamp": "2025-06-19"
    }), 200

# API info endpoint
@app.route('/api/info', methods=['GET'])
def api_info():
    """API information"""
    return jsonify({
        "name": "Facilitator Backend API",
        "version": "0.1.0",
        "authentication": "Phone OTP based",
        "status": "healthy"
    }), 200

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(facilitator_bp, url_prefix='/api/facilitator')
app.register_blueprint(offerings_bp, url_prefix='/api/offerings')

if __name__ == "__main__":
    app.run(debug=True)


