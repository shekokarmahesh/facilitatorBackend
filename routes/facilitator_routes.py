from flask import Blueprint, jsonify, request
from middleware.token_required import token_required
from models.database import DatabaseManager
import json
from datetime import datetime, timezone

facilitator_routes = Blueprint('facilitator_routes', __name__)
db_manager = DatabaseManager()

@facilitator_routes.route('/api/facilitator/profile', methods=['GET'])
@token_required
def get_profile():
    """Get facilitator profile"""
    try:
        # Get user info from token
        user_email = request.user_email
        
        # Get user_id from email
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Get facilitator profile
        db_manager.cursor.execute(
            "SELECT * FROM facilitator_profiles WHERE user_id = %s AND tenant_id = %s",
            (user_id, tenant_id)
        )
        profile = db_manager.cursor.fetchone()
        
        if not profile:
            return jsonify({"error": "Profile not found"}), 404
        
        return jsonify({
            "id": profile['id'],
            "user_id": profile['user_id'],
            "tenant_id": profile['tenant_id'],
            "basic_info": profile['basic_info'],
            "professional_details": profile['professional_details'],
            "bio_about": profile['bio_about'],
            "experience": profile['experience'],
            "certifications": profile['certifications'],
            "visual_profile": profile['visual_profile'],
            "created_at": profile['created_at'].isoformat(),
            "updated_at": profile['updated_at'].isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@facilitator_routes.route('/api/facilitator/profile', methods=['POST'])
@token_required
def create_profile():
    """Create facilitator profile"""
    try:
        data = request.json
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Check if profile already exists
        db_manager.cursor.execute(
            "SELECT id FROM facilitator_profiles WHERE user_id = %s AND tenant_id = %s",
            (user_id, tenant_id)
        )
        if db_manager.cursor.fetchone():
            return jsonify({"error": "Profile already exists"}), 400
        
        # Create profile
        db_manager.cursor.execute(
            """
            INSERT INTO facilitator_profiles 
            (tenant_id, user_id, basic_info, professional_details, bio_about, experience, certifications, visual_profile, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id;
            """,
            (
                tenant_id,
                user_id,
                json.dumps(data.get('basic_info', {})),
                json.dumps(data.get('professional_details', {})),
                json.dumps(data.get('bio_about', {})),
                json.dumps(data.get('experience', [])),
                json.dumps(data.get('certifications', [])),
                json.dumps(data.get('visual_profile', {}))
            )
        )
        
        profile_id = db_manager.cursor.fetchone()[0]
        db_manager.connection.commit()
        
        return jsonify({
            "message": "Profile created successfully",
            "profile_id": profile_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@facilitator_routes.route('/api/facilitator/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update entire facilitator profile"""
    try:
        data = request.json
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Update profile
        db_manager.cursor.execute(
            """
            UPDATE facilitator_profiles 
            SET basic_info = %s, professional_details = %s, bio_about = %s, 
                experience = %s, certifications = %s, visual_profile = %s, 
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND tenant_id = %s
            """,
            (
                json.dumps(data.get('basic_info', {})),
                json.dumps(data.get('professional_details', {})),
                json.dumps(data.get('bio_about', {})),
                json.dumps(data.get('experience', [])),
                json.dumps(data.get('certifications', [])),
                json.dumps(data.get('visual_profile', {})),
                user_id,
                tenant_id
            )
        )
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Profile updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@facilitator_routes.route('/api/facilitator/profile', methods=['DELETE'])
@token_required
def delete_profile():
    """Delete facilitator profile"""
    try:
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Delete profile
        db_manager.cursor.execute(
            "DELETE FROM facilitator_profiles WHERE user_id = %s AND tenant_id = %s",
            (user_id, tenant_id)
        )
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Profile deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Section-specific update endpoints
@facilitator_routes.route('/api/facilitator/profile/basic-info', methods=['PUT'])
@token_required
def update_basic_info():
    """Update basic info section"""
    try:
        data = request.json
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Update basic info
        db_manager.cursor.execute(
            """
            UPDATE facilitator_profiles 
            SET basic_info = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND tenant_id = %s
            """,
            (json.dumps(data), user_id, tenant_id)
        )
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Basic info updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@facilitator_routes.route('/api/facilitator/profile/professional-details', methods=['PUT'])
@token_required
def update_professional_details():
    """Update professional details section"""
    try:
        data = request.json
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Update professional details
        db_manager.cursor.execute(
            """
            UPDATE facilitator_profiles 
            SET professional_details = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND tenant_id = %s
            """,
            (json.dumps(data), user_id, tenant_id)
        )
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Professional details updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@facilitator_routes.route('/api/facilitator/profile/bio-about', methods=['PUT'])
@token_required
def update_bio_about():
    """Update bio/about section"""
    try:
        data = request.json
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Update bio/about
        db_manager.cursor.execute(
            """
            UPDATE facilitator_profiles 
            SET bio_about = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND tenant_id = %s
            """,
            (json.dumps(data), user_id, tenant_id)
        )
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Bio/about updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@facilitator_routes.route('/api/facilitator/profile/experience', methods=['PUT'])
@token_required
def update_experience():
    """Update experience section"""
    try:
        data = request.json
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Update experience
        db_manager.cursor.execute(
            """
            UPDATE facilitator_profiles 
            SET experience = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND tenant_id = %s
            """,
            (json.dumps(data), user_id, tenant_id)
        )
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Experience updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@facilitator_routes.route('/api/facilitator/profile/certifications', methods=['PUT'])
@token_required
def update_certifications():
    """Update certifications section"""
    try:
        data = request.json
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Update certifications
        db_manager.cursor.execute(
            """
            UPDATE facilitator_profiles 
            SET certifications = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND tenant_id = %s
            """,
            (json.dumps(data), user_id, tenant_id)
        )
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Certifications updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@facilitator_routes.route('/api/facilitator/profile/visual-profile', methods=['PUT'])
@token_required
def update_visual_profile():
    """Update visual profile section"""
    try:
        data = request.json
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Update visual profile
        db_manager.cursor.execute(
            """
            UPDATE facilitator_profiles 
            SET visual_profile = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND tenant_id = %s
            """,
            (json.dumps(data), user_id, tenant_id)
        )
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Visual profile updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
