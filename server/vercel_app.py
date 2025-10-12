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
CORS(app, origins="*")

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

# Basic user registration endpoint for testing
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Basic registration endpoint"""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"msg": "Username and password required", "status": False}), 400
        
        # For now, just return success - full implementation would use MongoDB
        return jsonify({
            "msg": "User registered successfully",
            "status": True
        }), 201
    except Exception as e:
        return jsonify({"msg": "Registration failed", "status": False}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Basic login endpoint"""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"msg": "Username and password required", "status": False}), 400
        
        # For now, just return test response
        return jsonify({
            "msg": "Login successful",
            "status": True,
            "user": {
                "_id": "test_user_id",
                "username": data.get('username'),
                "email": f"{data.get('username')}@test.com",
                "isAvatarImageSet": False,
                "avatarImage": ""
            }
        }), 200
    except Exception as e:
        return jsonify({"msg": "Login failed", "status": False}), 500

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