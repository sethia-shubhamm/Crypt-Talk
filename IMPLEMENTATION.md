# Crypt-Talk: End-to-End Encrypted Chat Application

## 🔒 Implementation Complete

I have successfully implemented the communication/chatting functionality with end-to-end encryption for your Crypt-Talk application. Here's what has been built:

## ✅ Implemented Features

### 1. **End-to-End Message Encryption**
- **Algorithm**: Fernet (AES 128) from Python's cryptography library
- **Key Generation**: SHA-256 hash of sorted user IDs ensures consistent encryption keys
- **Process**: Messages are encrypted before database storage and decrypted when retrieved
- **Security**: Each user pair has a unique encryption key

### 2. **Real-Time Messaging**
- **Technology**: Socket.IO for real-time communication
- **Features**: 
  - Instant message delivery
  - Online user tracking
  - Connection status management
  - Real-time typing indicators support

### 3. **Message Persistence**
- **Storage**: MongoDB with encrypted message content
- **Structure**: Messages stored with sender/receiver metadata
- **History**: Complete chat history with encryption/decryption on demand

### 4. **Authentication & Security**
- **Password Encryption**: bcrypt with salt for user passwords
- **Session Management**: Secure user sessions
- **User Management**: Registration, login, logout functionality

## 🏗️ Architecture

### Backend (Flask + Socket.IO)
```
server/app.py - Main application with:
├── Authentication routes (/api/auth/*)
├── Message routes (/api/messages/*)
├── Socket.IO handlers (real-time events)
├── Encryption/Decryption functions
└── MongoDB integration
```

### Frontend (React + Socket.IO Client)
```
public/src/
├── pages/Chat.jsx - Main chat interface
├── components/ChatContainer.jsx - Message display
├── components/ChatInput.jsx - Message input
├── components/Contacts.jsx - User list
└── utils/APIRoutes.js - API endpoints
```

## 🔐 Encryption Flow

### Message Sending:
1. User types message in frontend
2. Message sent via Socket.IO to backend
3. Backend encrypts message using user-pair key
4. Encrypted message stored in MongoDB
5. Message delivered to recipient if online

### Message Retrieval:
1. Frontend requests chat history
2. Backend retrieves encrypted messages from database
3. Messages decrypted using same user-pair key
4. Decrypted messages sent to frontend for display

## 🚀 Key Security Features

1. **Unique Encryption Keys**: Each user pair has a distinct encryption key
2. **Consistent Key Generation**: Keys are identical regardless of message direction
3. **No Plaintext Storage**: Messages never stored unencrypted in database
4. **Password Security**: User passwords hashed with bcrypt
5. **Session Security**: Secure user session management

## 📱 How to Run

### Backend:
```bash
cd server
pip install -r requirements.txt
python app.py
```

### Frontend:
```bash
cd public
npm install
npm start
```

### Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Test credentials: username='testuser', password='password123'

## 🛠️ Technologies Used

### Backend:
- **Flask**: Web framework
- **Flask-SocketIO**: Real-time communication
- **PyMongo**: MongoDB integration
- **Cryptography**: Message encryption (Fernet/AES)
- **bcrypt**: Password hashing

### Frontend:
- **React**: UI framework
- **Socket.IO Client**: Real-time messaging
- **Styled Components**: Styling
- **Axios**: HTTP requests

## 🔧 Database Schema

### Users Collection:
```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string", 
  "password": "hashed_password",
  "isAvatarImageSet": "boolean",
  "avatarImage": "base64_string"
}
```

### Messages Collection:
```json
{
  "_id": "ObjectId",
  "message": {
    "text": "encrypted_message_content",
    "users": ["sender_id", "receiver_id"]
  },
  "users": ["sender_id", "receiver_id"],
  "sender": "sender_id",
  "createdAt": "timestamp"
}
```

## 🎯 Demo

Run `python demo_encryption.py` to see the encryption/decryption functionality in action with sample messages between users.

## 🔒 Security Notes

1. **Production Considerations**:
   - Use environment variables for sensitive data
   - Implement rate limiting
   - Add input validation and sanitization
   - Use HTTPS in production
   - Implement proper error handling

2. **Encryption Strength**:
   - Fernet uses AES 128 in CBC mode with HMAC for authentication
   - Keys derived from SHA-256 hash of user pair
   - Each message has unique initialization vector

Your Crypt-Talk application now has full end-to-end encrypted messaging functionality with real-time communication capabilities!