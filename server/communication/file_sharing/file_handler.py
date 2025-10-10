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
from .seven_layer_file_encryption import encrypt_file_data, decrypt_file_data, encrypt_image_with_metadata, decrypt_image_with_metadata

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
            
            # 🔐 ENCRYPT FILE DATA
            if file_type == 'image':
                # Use specialized image encryption with metadata
                encryption_info = encrypt_image_with_metadata(
                    file_data, from_user, to_user, file.filename, file.content_type
                )
            else:
                # Use standard file encryption for PDFs and other files
                encryption_info = encrypt_file_data(file_data, from_user, to_user, file.filename)
            
            if not encryption_info:
                return jsonify({"msg": "File encryption failed", "status": False}), 500
            
            # Store encrypted file in MongoDB
            encrypted_data = base64.b64decode(encryption_info['encrypted_data'])
            
            file_document = {
                "filename": filename,
                "original_filename": file.filename,
                "file_type": file_type,
                "file_size": file_size,
                "file_data": encrypted_data,  # Store encrypted binary data
                "content_type": file.content_type,
                "uploaded_by": ObjectId(from_user),
                "shared_with": ObjectId(to_user),
                "users": [ObjectId(from_user), ObjectId(to_user)],
                "createdAt": datetime.utcnow(),
                "file_encryption": encryption_info,  # Store encryption metadata
                "is_encrypted": True
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
            
            # 🔓 DECRYPT FILE DATA
            if file_doc.get('is_encrypted', False):
                # Get user IDs for decryption
                user_ids = file_doc['users']
                user1_id = str(user_ids[0])
                user2_id = str(user_ids[1])
                
                if file_doc.get('file_type') == 'image':
                    # Decrypt image with metadata
                    decrypted_data, metadata = decrypt_image_with_metadata(
                        file_doc['file_encryption'], user1_id, user2_id
                    )
                    if decrypted_data is None:
                        return jsonify({"msg": "File decryption failed", "status": False}), 500
                else:
                    # Decrypt regular file
                    decrypted_data = decrypt_file_data(
                        file_doc['file_encryption'], user1_id, user2_id
                    )
                    if decrypted_data is None:
                        return jsonify({"msg": "File decryption failed", "status": False}), 500
                
                file_data = io.BytesIO(decrypted_data)
            else:
                # Unencrypted file (legacy support)
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
            
            # 🔓 DECRYPT IMAGE FOR PREVIEW
            if file_doc.get('is_encrypted', False):
                # Get user IDs for decryption
                user_ids = file_doc['users']
                user1_id = str(user_ids[0])
                user2_id = str(user_ids[1])
                
                # Decrypt image with metadata
                decrypted_data, metadata = decrypt_image_with_metadata(
                    file_doc['file_encryption'], user1_id, user2_id
                )
                
                if decrypted_data is None:
                    return jsonify({"msg": "Image decryption failed", "status": False}), 500
                
                # Use decrypted data and metadata
                file_data_b64 = base64.b64encode(decrypted_data).decode()
                content_type = metadata.get('content_type', file_doc['content_type'])
            else:
                # Unencrypted image (legacy support)
                file_data_b64 = base64.b64encode(file_doc['file_data']).decode()
                content_type = file_doc['content_type']
            
            return jsonify({
                "status": True,
                "filename": file_doc['original_filename'],
                "file_type": file_doc['file_type'],
                "content_type": content_type,
                "file_data": f"data:{content_type};base64,{file_data_b64}",
                "is_encrypted": file_doc.get('is_encrypted', False)
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
                "createdAt": file_doc['createdAt'].isoformat(),
                "is_encrypted": file_doc.get('is_encrypted', False)
            })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/files/encryption/stats', methods=['GET'])
    def get_file_encryption_stats_endpoint():
        """Get file encryption statistics"""
        try:
            from .seven_layer_file_encryption import get_file_encryption_stats
            stats = get_file_encryption_stats(mongo)
            
            return jsonify({
                "status": True,
                "encryption_stats": stats
            })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500
    
    @app.route('/api/files/encryption/migrate/<user1_id>/<user2_id>', methods=['POST'])
    def migrate_user_files(user1_id, user2_id):
        """Migrate unencrypted files to encrypted format for specific users"""
        try:
            from .seven_layer_file_encryption import migrate_existing_files_to_encryption
            
            limit = request.json.get('limit', 10) if request.json else 10
            migrated_count = migrate_existing_files_to_encryption(mongo, user1_id, user2_id, limit)
            
            return jsonify({
                "status": True,
                "message": f"Migration completed",
                "migrated_files": migrated_count
            })
        
        except Exception as e:
            return jsonify({"msg": f"Server error: {str(e)}", "status": False}), 500