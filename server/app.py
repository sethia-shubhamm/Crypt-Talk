from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
from bson.objectid import ObjectId
import bcrypt
import os
from dotenv import load_dotenv

# Import communication modules
from communication.messaging.message_handler import create_message_routes
from communication.socketio.socket_handler import create_socketio_handlers, remove_user_from_online

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")

# Socket.IO configuration
socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URL")
mongo = PyMongo(app)

print("✅ Connected to MongoDB")

# Helper function to serialize MongoDB objects
def serialize_user(user):
    if user:
        user['_id'] = str(user['_id'])
        return user
    return None

def serialize_users(users):
    return [serialize_user(user) for user in users]

# Helper functions for database operations
def find_user_by_username(username):
    return mongo.db.users.find_one({"username": username})

def find_user_by_email(email):
    return mongo.db.users.find_one({"email": email})

def find_user_by_id(user_id):
    try:
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})
    except:
        return None

# Initialize with one test user
def init_test_user():
    """Create a default test user for easy testing"""
    existing_user = mongo.db.users.find_one({"username": "testuser"})
    if not existing_user:
        hashed_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt())
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": hashed_password,
            "isAvatarImageSet": False,
            "avatarImage": ""
        }
        mongo.db.users.insert_one(test_user)
        print("✅ Test user created: username='testuser', password='password123'")
    else:
        print("✅ Test user already exists: username='testuser', password='password123'")

# Routes
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Python Flask backend is running!"})

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Check if username already exists
        if find_user_by_username(username):
            return jsonify({"msg": "Username already used", "status": False})
        
        # Check if email already exists
        if find_user_by_email(email):
            return jsonify({"msg": "Email already used", "status": False})
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_data = {
            "email": email,
            "username": username,
            "password": hashed_password,
            "isAvatarImageSet": False,
            "avatarImage": ""
        }
        
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = str(result.inserted_id)
        
        # Remove password from response
        del user_data['password']
        
        return jsonify({"status": True, "user": user_data})
    
    except Exception as e:
        return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Find user by username
        user = find_user_by_username(username)
        if not user:
            return jsonify({"msg": "Incorrect Username or Password", "status": False})
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return jsonify({"msg": "Incorrect Username or Password", "status": False})
        
        # Remove password from response
        user = serialize_user(user)
        del user['password']
        
        return jsonify({"status": True, "user": user})
    
    except Exception as e:
        return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500

@app.route('/api/auth/allusers/<user_id>', methods=['GET'])
def get_all_users(user_id):
    try:
        # Get all users except the current user
        users = mongo.db.users.find(
            {"_id": {"$ne": ObjectId(user_id)}},
            {"email": 1, "username": 1, "avatarImage": 1, "_id": 1}
        )
        
        users_list = serialize_users(list(users))
        return jsonify(users_list)
    
    except Exception as e:
        return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500

@app.route('/api/auth/setavatar/<user_id>', methods=['POST'])
def set_avatar(user_id):
    try:
        data = request.get_json()
        avatar_image = data.get('image')
        
        # Update user avatar
        result = mongo.db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {"isAvatarImageSet": True, "avatarImage": avatar_image}},
            return_document=True
        )
        
        if result:
            return jsonify({
                "isSet": result.get("isAvatarImageSet", False),
                "image": result.get("avatarImage", "")
            })
        else:
            return jsonify({"msg": "User not found", "status": False}), 404
    
    except Exception as e:
        return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500

@app.route('/api/auth/logout/<user_id>', methods=['GET'])
def logout(user_id):
    try:
        if not user_id:
            return jsonify({"msg": "User id is required"}), 400
        
        # Remove user from online users using communication module
        remove_user_from_online(user_id)
        
        return '', 200
    
    except Exception as e:
        return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500

if __name__ == '__main__':
    # Initialize test user on startup
    init_test_user()
    
    # Initialize communication modules
    create_message_routes(app, mongo)
    create_socketio_handlers(socketio)
    
    port = int(os.environ.get("PORT", 5000))
    is_production = os.getenv("FLASK_ENV") == "production"
    
    print(f"🚀 Starting server with Socket.IO on port {port}")
    print(" Test user: username='testuser', password='password123'")
    print("🔒 End-to-end encryption enabled for messages")
    print("📁 Communication modules loaded from /communication folder")
    
    if is_production:
        print("🌐 Running in PRODUCTION mode")
    else:
        print("🛠️ Running in DEVELOPMENT mode")
        print("📱 Frontend: http://localhost:3000")
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=not is_production,
        allow_unsafe_werkzeug=True
    )