"""
Vercel-compatible entry point for Crypt-Talk backend server
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging

# Suppress warnings and reduce logging noise
logging.getLogger('werkzeug').setLevel(logging.ERROR)
os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# Configure CORS more explicitly - allow all origins
CORS(app, 
     origins="*",
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=False)

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Crypt-Talk Backend",
        "version": "1.0.0"
    })

@app.route('/api/test')
def test_endpoint():
    """Test API endpoint"""
    return jsonify({
        "message": "API is working",
        "status": "success"
    })

# Handle all CORS in one place
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    response.headers.add("Access-Control-Max-Age", "3600")
    return response

# Handle preflight OPTIONS requests for all routes
@app.route('/<path:path>', methods=['OPTIONS'])
@app.route('/', methods=['OPTIONS'])
def handle_options(path=None):
    return '', 200

# Basic user registration endpoint for testing
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Basic registration endpoint"""
        
    try:
        data = request.get_json()
        print(f"Registration attempt with data: {data}")  # Debug log
        
        if not data or not data.get('username') or not data.get('password') or not data.get('email'):
            return jsonify({
                "msg": "Username, email and password required", 
                "status": False
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        # Simple validation for demo
        if len(username) < 3:
            return jsonify({
                "msg": "Username must be at least 3 characters", 
                "status": False
            }), 400
            
        if len(password) < 6:
            return jsonify({
                "msg": "Password must be at least 6 characters", 
                "status": False
            }), 400
        
        # For now, just return success - full implementation would use MongoDB
        return jsonify({
            "msg": "User registered successfully",
            "status": True,
            "user": {
                "_id": f"user_{username}",
                "username": username,
                "email": email,
                "isAvatarImageSet": False,
                "avatarImage": ""
            }
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Debug log
        return jsonify({
            "msg": f"Registration failed: {str(e)}", 
            "status": False
        }), 500

@app.route('/api/auth/allusers/<user_id>', methods=['GET'])
def get_all_users(user_id):
    """Get all users except current user"""
    try:
        # Return some dummy users for testing
        users = [
            {
                "_id": "user_testuser1",
                "username": "testuser1",
                "email": "testuser1@crypttalk.com",
                "avatarImage": "",
                "isAvatarImageSet": False
            },
            {
                "_id": "user_testuser2", 
                "username": "testuser2",
                "email": "testuser2@crypttalk.com",
                "avatarImage": "",
                "isAvatarImageSet": False
            }
        ]
        
        # Filter out current user
        filtered_users = [user for user in users if user["_id"] != user_id]
        
        return jsonify(filtered_users), 200
        
    except Exception as e:
        print(f"Get users error: {str(e)}")
        return jsonify({"error": f"Failed to get users: {str(e)}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Basic login endpoint"""
        
    try:
        data = request.get_json()
        print(f"Login attempt with data: {data}")  # Debug log
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                "msg": "Username and password required", 
                "status": False,
                "user": None
            }), 400
        
        # For testing - accept any username/password
        username = data.get('username')
        password = data.get('password')
        
        # Simple validation for demo
        if len(username) < 3:
            return jsonify({
                "msg": "Username must be at least 3 characters", 
                "status": False,
                "user": None
            }), 400
            
        if len(password) < 6:
            return jsonify({
                "msg": "Password must be at least 6 characters", 
                "status": False,
                "user": None
            }), 400
        
        # For now, just return test response with proper user data
        return jsonify({
            "msg": "Login successful",
            "status": True,
            "user": {
                "_id": f"user_{username}",
                "username": username,
                "email": f"{username}@crypttalk.com",
                "isAvatarImageSet": False,
                "avatarImage": ""
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        return jsonify({
            "msg": f"Login failed: {str(e)}", 
            "status": False,
            "user": None
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# For Vercel deployment
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)