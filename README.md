# Crypt-Talk - Secure Chat Application

## Overview
A secure real-time chat application with end-to-end encryption, file sharing, and self-destruct capabilities.

## Core Features
- **Secure Messaging**: Fernet (AES-128) encryption for all messages
- **File Encryption**: Separate encrypted file sharing system
- **Password Security**: bcrypt hashing with salt generation
- **Self-Destruct**: Automatic conversation deletion
- **Real-time**: Socket.IO for instant messaging

## Project Structure
```
server/
├── app.py                    # Main Flask application
├── communication/
│   ├── encryption/          # Message encryption
│   ├── file_sharing/        # File encryption & handling
│   ├── messaging/           # Message handling
│   ├── socketio/            # Real-time communication
│   └── self_destruct/       # Timer functionality
└── requirements.txt         # Python dependencies

public/
├── src/
│   ├── components/          # React components
│   ├── pages/              # Application pages
│   └── utils/              # Client utilities
└── package.json            # Node.js dependencies
```

## Setup Instructions
1. **Backend**: `cd server && pip install -r requirements.txt && python app.py`
2. **Frontend**: `cd public && npm install && npm start`
3. **Database**: MongoDB required
4. **Access**: http://localhost:3000

## Security Features
- All messages encrypted with Fernet (AES-128 + HMAC-SHA256)
- Files encrypted with separate key namespace
- Passwords hashed with bcrypt
- Real-time encryption logging
- Automatic data deletion with self-destruct timers

## API Endpoints
- Authentication: `/api/auth/login`, `/api/auth/register`
- Messages: `/api/messages/addmsg`, `/api/messages/getmsg`
- Files: `/api/files/upload`, `/api/files/download`
- Self-destruct: `/api/self-destruct/*`