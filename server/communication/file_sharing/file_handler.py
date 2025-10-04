"""
File Handler Module for Crypt-Talk
Handles file upload, storage, and retrieval for PDF and image files
"""

from flask import request, jsonify, send_file
from bson.objectid import ObjectId
from datetime import datetime
import base64
import io
import os
from werkzeug.utils import secure_filename
from ..self_destruct.timer_handler import add_self_destruct_to_message

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf': ['pdf'],
    'images': ['png', 'jpg', 'jpeg', 'gif', 'webp']
}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

def allowed_file(filename, file_type='all'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'pdf':
        return extension in ALLOWED_EXTENSIONS['pdf']
    elif file_type == 'images':
        return extension in ALLOWED_EXTENSIONS['images']
    else:
        # Allow both PDF and images
        all_extensions = ALLOWED_EXTENSIONS['pdf'] + ALLOWED_EXTENSIONS['images']
        return extension in all_extensions

def get_file_type(filename):
    """Get file type based on extension"""
    if '.' not in filename:
        return 'unknown'
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension in ALLOWED_EXTENSIONS['pdf']:
        return 'pdf'
    elif extension in ALLOWED_EXTENSIONS['images']:
        return 'image'
    else:
        return 'unknown'

def create_file_routes(app, mongo):
    """Create Flask routes for file handling"""
    
    @app.route('/api/files/upload', methods=['POST'])
    def upload_file():
        try:
            # Check if file is in request
            if 'file' not in request.files:
                return jsonify({"msg": "No file provided", "status": False}), 400
            
            file = request.files['file']
            from_user = request.form.get('from')
            to_user = request.form.get('to')
            
            if not from_user or not to_user:
                return jsonify({"msg": "Missing user information", "status": False}), 400
            
            if file.filename == '':
                return jsonify({"msg": "No file selected", "status": False}), 400
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Reset file pointer
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({"msg": f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB", "status": False}), 400
            
            # Check if file type is allowed
            if not allowed_file(file.filename):
                return jsonify({"msg": "File type not allowed. Only PDF and images are supported.", "status": False}), 400
            
            # Get file info
            filename = secure_filename(file.filename)
            file_type = get_file_type(filename)
            file_data = file.read()
            
            # Store file in MongoDB
            file_document = {
                "filename": filename,
                "original_filename": file.filename,
                "file_type": file_type,
                "file_size": file_size,
                "file_data": file_data,  # Store binary data directly
                "content_type": file.content_type,
                "uploaded_by": ObjectId(from_user),
                "shared_with": ObjectId(to_user),
                "users": [ObjectId(from_user), ObjectId(to_user)],
                "createdAt": datetime.utcnow()
            }
            
            result = mongo.db.files.insert_one(file_document)
            
            # Create a message entry for the file
            message_data = {
                "message": {
                    "type": "file",
                    "file_id": result.inserted_id,
                    "filename": filename,
                    "original_filename": file.filename,
                    "file_type": file_type,
                    "file_size": file_size,
                    "users": [ObjectId(from_user), ObjectId(to_user)]
                },
                "users": [ObjectId(from_user), ObjectId(to_user)],
                "sender": ObjectId(from_user),
                "createdAt": datetime.utcnow()
            }
            
            # Add self-destruct timer if user has one configured
            message_data = add_self_destruct_to_message(message_data, from_user, mongo)
            
            message_result = mongo.db.messages.insert_one(message_data)
            
            return jsonify({
                "msg": "File uploaded successfully",
                "status": True,
                "file_id": str(result.inserted_id),
                "message_id": str(message_result.inserted_id),
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size
            })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/files/download/<file_id>', methods=['GET'])
    def download_file(file_id):
        try:
            # Get file from database
            file_doc = mongo.db.files.find_one({"_id": ObjectId(file_id)})
            
            if not file_doc:
                return jsonify({"msg": "File not found", "status": False}), 404
            
            # Create file-like object from binary data
            file_data = io.BytesIO(file_doc['file_data'])
            
            return send_file(
                file_data,
                as_attachment=True,
                download_name=file_doc['original_filename'],
                mimetype=file_doc['content_type']
            )
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/files/preview/<file_id>', methods=['GET'])
    def preview_file(file_id):
        try:
            # Get file from database
            file_doc = mongo.db.files.find_one({"_id": ObjectId(file_id)})
            
            if not file_doc:
                return jsonify({"msg": "File not found", "status": False}), 404
            
            # Only allow preview for images
            if file_doc['file_type'] != 'image':
                return jsonify({"msg": "Preview only available for images", "status": False}), 400
            
            # Return base64 encoded image for preview
            file_data_b64 = base64.b64encode(file_doc['file_data']).decode()
            
            return jsonify({
                "status": True,
                "filename": file_doc['original_filename'],
                "file_type": file_doc['file_type'],
                "content_type": file_doc['content_type'],
                "file_data": f"data:{file_doc['content_type']};base64,{file_data_b64}"
            })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/files/info/<file_id>', methods=['GET'])
    def get_file_info(file_id):
        try:
            # Get file info from database (without file data)
            file_doc = mongo.db.files.find_one(
                {"_id": ObjectId(file_id)},
                {"file_data": 0}  # Exclude file data from result
            )
            
            if not file_doc:
                return jsonify({"msg": "File not found", "status": False}), 404
            
            return jsonify({
                "status": True,
                "file_id": str(file_doc['_id']),
                "filename": file_doc['filename'],
                "original_filename": file_doc['original_filename'],
                "file_type": file_doc['file_type'],
                "file_size": file_doc['file_size'],
                "content_type": file_doc['content_type'],
                "uploaded_by": str(file_doc['uploaded_by']),
                "createdAt": file_doc['createdAt'].isoformat()
            })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500