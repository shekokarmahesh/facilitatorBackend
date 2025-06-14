from flask import Blueprint, jsonify, request
from middleware.token_required import token_required
from models.database import DatabaseManager
import json
from datetime import datetime, timezone

offerings_routes = Blueprint('offerings_routes', __name__)
db_manager = DatabaseManager()

@offerings_routes.route('/api/offerings', methods=['GET'])
@token_required
def get_offerings():
    """Get all offerings for the authenticated user"""
    try:
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Get query parameters for filtering
        status = request.args.get('status')
        offering_type = request.args.get('type')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Build query
        query = "SELECT * FROM offerings WHERE user_id = %s AND tenant_id = %s"
        params = [user_id, tenant_id]
        
        if status:
            query += " AND basic_info->>'status' = %s"
            params.append(status)
        
        if offering_type:
            query += " AND basic_info->>'type' = %s"
            params.append(offering_type)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, (page - 1) * limit])
        
        db_manager.cursor.execute(query, params)
        offerings = db_manager.cursor.fetchall()
        
        # Format response
        result = []
        for offering in offerings:
            result.append({
                "id": offering['id'],
                "user_id": offering['user_id'],
                "tenant_id": offering['tenant_id'],
                "basic_info": offering['basic_info'],
                "details": offering['details'],
                "price_schedule": offering['price_schedule'],
                "created_at": offering['created_at'].isoformat(),
                "updated_at": offering['updated_at'].isoformat()
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offerings_routes.route('/api/offerings', methods=['POST'])
@token_required
def create_offering():
    """Create new offering"""
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
        
        # Create offering
        db_manager.cursor.execute(
            """
            INSERT INTO offerings 
            (tenant_id, user_id, basic_info, details, price_schedule, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id;
            """,
            (
                tenant_id,
                user_id,
                json.dumps(data.get('basic_info', {})),
                json.dumps(data.get('details', {})),
                json.dumps(data.get('price_schedule', {}))
            )
        )
        
        offering_id = db_manager.cursor.fetchone()[0]
        db_manager.connection.commit()
        
        return jsonify({
            "message": "Offering created successfully",
            "offering_id": offering_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offerings_routes.route('/api/offerings/<int:offering_id>', methods=['GET'])
@token_required
def get_offering(offering_id):
    """Get specific offering"""
    try:
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Get offering
        db_manager.cursor.execute(
            "SELECT * FROM offerings WHERE id = %s AND user_id = %s AND tenant_id = %s",
            (offering_id, user_id, tenant_id)
        )
        offering = db_manager.cursor.fetchone()
        
        if not offering:
            return jsonify({"error": "Offering not found"}), 404
        
        return jsonify({
            "id": offering['id'],
            "user_id": offering['user_id'],
            "tenant_id": offering['tenant_id'],
            "basic_info": offering['basic_info'],
            "details": offering['details'],
            "price_schedule": offering['price_schedule'],
            "created_at": offering['created_at'].isoformat(),
            "updated_at": offering['updated_at'].isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offerings_routes.route('/api/offerings/<int:offering_id>', methods=['PUT'])
@token_required
def update_offering(offering_id):
    """Update entire offering"""
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
        
        # Update offering
        db_manager.cursor.execute(
            """
            UPDATE offerings 
            SET basic_info = %s, details = %s, price_schedule = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s AND tenant_id = %s
            """,
            (
                json.dumps(data.get('basic_info', {})),
                json.dumps(data.get('details', {})),
                json.dumps(data.get('price_schedule', {})),
                offering_id,
                user_id,
                tenant_id
            )
        )
        
        if db_manager.cursor.rowcount == 0:
            return jsonify({"error": "Offering not found"}), 404
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Offering updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offerings_routes.route('/api/offerings/<int:offering_id>', methods=['DELETE'])
@token_required
def delete_offering(offering_id):
    """Delete offering"""
    try:
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Delete offering
        db_manager.cursor.execute(
            "DELETE FROM offerings WHERE id = %s AND user_id = %s AND tenant_id = %s",
            (offering_id, user_id, tenant_id)
        )
        
        if db_manager.cursor.rowcount == 0:
            return jsonify({"error": "Offering not found"}), 404
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Offering deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Status management endpoints
@offerings_routes.route('/api/offerings/<int:offering_id>/publish', methods=['PUT'])
@token_required
def publish_offering(offering_id):
    """Publish offering"""
    try:
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Update status to published
        db_manager.cursor.execute(
            """
            UPDATE offerings 
            SET basic_info = jsonb_set(basic_info, '{status}', '"Published"', true),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s AND tenant_id = %s
            """,
            (offering_id, user_id, tenant_id)
        )
        
        if db_manager.cursor.rowcount == 0:
            return jsonify({"error": "Offering not found"}), 404
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Offering published successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offerings_routes.route('/api/offerings/<int:offering_id>/archive', methods=['PUT'])
@token_required
def archive_offering(offering_id):
    """Archive offering"""
    try:
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Update status to archived
        db_manager.cursor.execute(
            """
            UPDATE offerings 
            SET basic_info = jsonb_set(basic_info, '{status}', '"Archived"', true),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s AND tenant_id = %s
            """,
            (offering_id, user_id, tenant_id)
        )
        
        if db_manager.cursor.rowcount == 0:
            return jsonify({"error": "Offering not found"}), 404
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Offering archived successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offerings_routes.route('/api/offerings/<int:offering_id>/draft', methods=['PUT'])
@token_required
def draft_offering(offering_id):
    """Set offering to draft"""
    try:
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Update status to draft
        db_manager.cursor.execute(
            """
            UPDATE offerings 
            SET basic_info = jsonb_set(basic_info, '{status}', '"Draft"', true),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s AND tenant_id = %s
            """,
            (offering_id, user_id, tenant_id)
        )
        
        if db_manager.cursor.rowcount == 0:
            return jsonify({"error": "Offering not found"}), 404
        
        db_manager.connection.commit()
        
        return jsonify({"message": "Offering set to draft successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offerings_routes.route('/api/offerings/duplicate/<int:offering_id>', methods=['POST'])
@token_required
def duplicate_offering(offering_id):
    """Duplicate offering"""
    try:
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Get original offering
        db_manager.cursor.execute(
            "SELECT * FROM offerings WHERE id = %s AND user_id = %s AND tenant_id = %s",
            (offering_id, user_id, tenant_id)
        )
        original = db_manager.cursor.fetchone()
        
        if not original:
            return jsonify({"error": "Offering not found"}), 404
        
        # Modify basic info to indicate copy
        basic_info = original['basic_info']
        if isinstance(basic_info, dict):
            basic_info['title'] = f"Copy of {basic_info.get('title', 'Untitled')}"
            basic_info['status'] = 'Draft'
        
        # Create duplicate
        db_manager.cursor.execute(
            """
            INSERT INTO offerings 
            (tenant_id, user_id, basic_info, details, price_schedule, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id;
            """,
            (
                tenant_id,
                user_id,
                json.dumps(basic_info),
                json.dumps(original['details']),
                json.dumps(original['price_schedule'])
            )
        )
        
        new_offering_id = db_manager.cursor.fetchone()[0]
        db_manager.connection.commit()
        
        return jsonify({
            "message": "Offering duplicated successfully",
            "offering_id": new_offering_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offerings_routes.route('/api/offerings/search', methods=['GET'])
@token_required
def search_offerings():
    """Search offerings"""
    try:
        user_email = request.user_email
        
        # Get user info
        db_manager.cursor.execute("SELECT id, tenant_id FROM users WHERE email = %s", (user_email,))
        user = db_manager.cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_id = user['id']
        tenant_id = user['tenant_id']
        
        # Get query parameters
        query = request.args.get('q', '')
        status = request.args.get('status')
        offering_type = request.args.get('type')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Build search query
        sql_query = """
            SELECT * FROM offerings 
            WHERE user_id = %s AND tenant_id = %s
        """
        params = [user_id, tenant_id]
        
        if query:
            sql_query += " AND (basic_info->>'title' ILIKE %s OR basic_info->>'description' ILIKE %s)"
            params.extend([f'%{query}%', f'%{query}%'])
        
        if status:
            sql_query += " AND basic_info->>'status' = %s"
            params.append(status)
        
        if offering_type:
            sql_query += " AND basic_info->>'type' = %s"
            params.append(offering_type)
        
        sql_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, (page - 1) * limit])
        
        db_manager.cursor.execute(sql_query, params)
        offerings = db_manager.cursor.fetchall()
        
        # Format response
        result = []
        for offering in offerings:
            result.append({
                "id": offering['id'],
                "user_id": offering['user_id'],
                "tenant_id": offering['tenant_id'],
                "basic_info": offering['basic_info'],
                "details": offering['details'],
                "price_schedule": offering['price_schedule'],
                "created_at": offering['created_at'].isoformat(),
                "updated_at": offering['updated_at'].isoformat()
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@offerings_routes.route('/api/offerings/categories', methods=['GET'])
@token_required
def get_categories():
    """Get available categories"""
    categories = [
        "Yoga",
        "Meditation",
        "Breathwork",
        "Fitness",
        "Wellness",
        "Mindfulness",
        "Spiritual",
        "Workshop",
        "Retreat",
        "Training"
    ]
    return jsonify(categories)

@offerings_routes.route('/api/offerings/tags', methods=['GET'])
@token_required
def get_tags():
    """Get available tags"""
    tags = [
        "Beginner Friendly",
        "Advanced",
        "Online",
        "Offline",
        "Group Session",
        "Individual",
        "Morning",
        "Evening",
        "Weekend",
        "Intensive",
        "Certification",
        "Holistic Health"
    ]
    return jsonify(tags)
