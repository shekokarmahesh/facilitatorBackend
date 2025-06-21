from flask import Blueprint, request, jsonify, session
from models.database import DatabaseManager, FacilitatorRepository
from middleware.session_required import session_required, onboarding_session_required
import logging

# Create blueprint
facilitator_bp = Blueprint('facilitator', __name__)

# Initialize database
db_manager = DatabaseManager()
facilitator_repo = FacilitatorRepository(db_manager)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================================================================
# FACILITATOR PROFILE MANAGEMENT ENDPOINTS
# ================================================================================

@facilitator_bp.route('/profile', methods=['GET'])
@session_required
def get_facilitator_profile():
    """Get current facilitator's complete profile"""
    try:
        facilitator_id = request.facilitator_id
        
        profile = facilitator_repo.get_facilitator_profile(facilitator_id)
        
        if not profile:
            return jsonify({
                "error": "Profile not found",
                "message": "Facilitator profile not found"
            }), 404
        
        return jsonify({
            "success": True,
            "profile": profile
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching facilitator profile: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch profile"
        }), 500

@facilitator_bp.route('/profile', methods=['PUT'])
@session_required
def update_facilitator_profile():
    """Update current facilitator's profile"""
    try:
        facilitator_id = request.facilitator_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Request body is required"
            }), 400
        
        # Prepare update data with all possible fields
        update_data = {
            "email": data.get("email"),
            "name": data.get("name"),
            "basic_info": data.get("basic_info"),
            "professional_details": data.get("professional_details"),
            "bio_about": data.get("bio_about"),
            "experience": data.get("experience"),
            "certifications": data.get("certifications"),
            "visual_profile": data.get("visual_profile")
        }
        
        # Update the profile
        facilitator_repo.update_facilitator_profile(facilitator_id, update_data)
        
        # Return updated profile
        updated_profile = facilitator_repo.get_facilitator_profile(facilitator_id)
        
        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "profile": updated_profile
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating facilitator profile: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to update profile"
        }), 500

@facilitator_bp.route('/profile/section', methods=['PUT'])
@session_required
def update_profile_section():
    """Update a specific section of the facilitator's profile"""
    try:
        facilitator_id = request.facilitator_id
        data = request.get_json()
        
        if not data or 'section' not in data:
            return jsonify({
                "error": "Invalid data",
                "message": "Section name and data are required"
            }), 400
        
        section = data.get('section')
        section_data = data.get('data')
        
        # Validate section name
        valid_sections = [
            'basic_info', 'professional_details', 'bio_about', 
            'experience', 'certifications', 'visual_profile'
        ]
        
        if section not in valid_sections:
            return jsonify({
                "error": "Invalid section",
                "message": f"Section must be one of: {', '.join(valid_sections)}"
            }), 400
        
        # Prepare update data for the specific section
        update_data = {section: section_data}
        
        # Update the profile section
        facilitator_repo.update_facilitator_profile(facilitator_id, update_data)
        
        return jsonify({
            "success": True,
            "message": f"Profile section '{section}' updated successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating profile section: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to update profile section"
        }), 500

# ================================================================================
# OFFERING MANAGEMENT ENDPOINTS
# ================================================================================

@facilitator_bp.route('/offerings', methods=['GET'])
@session_required
def get_facilitator_offerings():
    """Get all offerings for the current facilitator"""
    try:
        facilitator_id = request.facilitator_id
        
        offerings = facilitator_repo.get_facilitator_offerings(facilitator_id)
        
        return jsonify({
            "success": True,
            "offerings": offerings,
            "count": len(offerings)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching facilitator offerings: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch offerings"
        }), 500

@facilitator_bp.route('/offerings', methods=['POST'])
@session_required
def create_offering():
    """Create a new offering for the current facilitator"""
    try:
        facilitator_id = request.facilitator_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Request body is required"
            }), 400
        
        # Validate required fields
        required_fields = ['title']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "error": f"Missing required field",
                    "message": f"Field '{field}' is required"
                }), 400
        
        # Prepare offering data
        offering_data = {
            "title": data.get("title"),
            "description": data.get("description"),
            "category": data.get("category"),
            "basic_info": data.get("basic_info"),
            "details": data.get("details"),
            "price_schedule": data.get("price_schedule")
        }
        
        # Create the offering
        offering_id = facilitator_repo.create_offering(facilitator_id, offering_data)
        
        if not offering_id:
            return jsonify({
                "error": "Creation failed",
                "message": "Failed to create offering"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "Offering created successfully",
            "offering_id": offering_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating offering: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to create offering"
        }), 500

@facilitator_bp.route('/offerings/<int:offering_id>', methods=['GET'])
@session_required
def get_offering_details():
    """Get details of a specific offering (must belong to current facilitator)"""
    try:
        facilitator_id = request.facilitator_id
        offering_id = request.view_args['offering_id']
        
        # Verify ownership
        if not facilitator_repo.verify_offering_ownership(facilitator_id, offering_id):
            return jsonify({
                "error": "Access denied",
                "message": "You don't have permission to access this offering"
            }), 403
        
        # Get offering details from the facilitator's offerings
        offerings = facilitator_repo.get_facilitator_offerings(facilitator_id)
        offering = next((o for o in offerings if o['id'] == offering_id), None)
        
        if not offering:
            return jsonify({
                "error": "Offering not found",
                "message": "Offering not found"
            }), 404
        
        return jsonify({
            "success": True,
            "offering": offering
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching offering details: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch offering details"
        }), 500

@facilitator_bp.route('/offerings/<int:offering_id>', methods=['PUT'])
@session_required
def update_offering():
    """Update a specific offering (must belong to current facilitator)"""
    try:
        facilitator_id = request.facilitator_id
        offering_id = request.view_args['offering_id']
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Request body is required"
            }), 400
        
        # Verify ownership
        if not facilitator_repo.verify_offering_ownership(facilitator_id, offering_id):
            return jsonify({
                "error": "Access denied",
                "message": "You don't have permission to update this offering"
            }), 403
        
        # Prepare update data
        update_data = {
            "title": data.get("title"),
            "description": data.get("description"),
            "category": data.get("category"),
            "basic_info": data.get("basic_info"),
            "details": data.get("details"),
            "price_schedule": data.get("price_schedule")
        }
        
        # Update the offering
        facilitator_repo.update_offering(offering_id, update_data)
        
        return jsonify({
            "success": True,
            "message": "Offering updated successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating offering: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to update offering"
        }), 500

@facilitator_bp.route('/offerings/<int:offering_id>', methods=['DELETE'])
@session_required
def delete_offering():
    """Soft delete a specific offering (must belong to current facilitator)"""
    try:
        facilitator_id = request.facilitator_id
        offering_id = request.view_args['offering_id']
        
        # Verify ownership
        if not facilitator_repo.verify_offering_ownership(facilitator_id, offering_id):
            return jsonify({
                "error": "Access denied",
                "message": "You don't have permission to delete this offering"
            }), 403
        
        # Soft delete by setting is_active to False
        update_data = {"is_active": False}
        facilitator_repo.update_offering(offering_id, {"is_active": False})
        
        return jsonify({
            "success": True,
            "message": "Offering deleted successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting offering: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to delete offering"
        }), 500

# ================================================================================
# PUBLIC SEARCH ENDPOINTS (No authentication required)
# ================================================================================

@facilitator_bp.route('/search', methods=['GET'])
def search_facilitators():
    """Public endpoint to search facilitators"""
    try:
        # Get query parameters
        name = request.args.get('name', '')
        email = request.args.get('email', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        # Prepare filters
        filters = {}
        if name:
            filters['name'] = name
        if email:
            filters['email'] = email
        
        # Search facilitators
        facilitators = facilitator_repo.search_facilitators(filters, page, limit)
        
        return jsonify({
            "success": True,
            "facilitators": facilitators,
            "pagination": {
                "page": page,
                "limit": limit,
                "count": len(facilitators)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching facilitators: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to search facilitators"
        }), 500

@facilitator_bp.route('/offerings/search', methods=['GET'])
def search_offerings():
    """Public endpoint to search offerings"""
    try:
        # Get query parameters
        title = request.args.get('title', '')
        description = request.args.get('description', '')
        category = request.args.get('category', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        # Prepare filters
        filters = {}
        if title:
            filters['title'] = title
        if description:
            filters['description'] = description
        if category:
            filters['category'] = category
        
        # Search offerings
        offerings = facilitator_repo.search_offerings(filters, page, limit)
        
        return jsonify({
            "success": True,
            "offerings": offerings,
            "pagination": {
                "page": page,
                "limit": limit,
                "count": len(offerings)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching offerings: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to search offerings"
        }), 500

# ================================================================================
# DASHBOARD ENDPOINTS
# ================================================================================

@facilitator_bp.route('/dashboard', methods=['GET'])
@session_required
def get_dashboard_data():
    """Get dashboard data for the current facilitator"""
    try:
        facilitator_id = request.facilitator_id
        
        # Get facilitator profile
        profile = facilitator_repo.get_facilitator_profile(facilitator_id)
        
        # Get facilitator offerings
        offerings = facilitator_repo.get_facilitator_offerings(facilitator_id)
        
        # Prepare dashboard data
        dashboard_data = {
            "profile": profile,
            "offerings": {
                "total": len(offerings),
                "active": len([o for o in offerings if o.get('is_active', True)]),
                "items": offerings
            },
            "session_info": {
                "facilitator_id": facilitator_id,
                "phone_number": request.phone_number,
                "authenticated": True
            }
        }
        
        return jsonify({
            "success": True,
            "dashboard": dashboard_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch dashboard data"
        }), 500

# ================================================================================
# UTILITY ENDPOINTS
# ================================================================================

@facilitator_bp.route('/profile/check-completeness', methods=['GET'])
@session_required
def check_profile_completeness():
    """Check how complete the facilitator's profile is"""
    try:
        facilitator_id = request.facilitator_id
        
        profile = facilitator_repo.get_facilitator_profile(facilitator_id)
        
        if not profile:
            return jsonify({
                "error": "Profile not found",
                "message": "Facilitator profile not found"
            }), 404
        
        # Define required fields for completeness
        required_fields = ['name', 'email']
        optional_sections = [
            'basic_info', 'professional_details', 'bio_about',
            'experience', 'certifications', 'visual_profile'
        ]
        
        # Check completeness
        completeness = {
            "required_fields_complete": all(profile.get(field) for field in required_fields),
            "completed_sections": [],
            "missing_sections": [],
            "overall_percentage": 0
        }
        
        # Check optional sections
        for section in optional_sections:
            if profile.get(section):
                completeness["completed_sections"].append(section)
            else:
                completeness["missing_sections"].append(section)
        
        # Calculate percentage
        total_items = len(required_fields) + len(optional_sections)
        completed_items = len([f for f in required_fields if profile.get(f)]) + len(completeness["completed_sections"])
        completeness["overall_percentage"] = int((completed_items / total_items) * 100)
        
        return jsonify({
            "success": True,
            "completeness": completeness
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking profile completeness: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to check profile completeness"
        }), 500
