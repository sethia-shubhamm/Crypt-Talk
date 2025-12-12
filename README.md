# 🔐 Crypt-Talk - Secure Real-Time Chat Application

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9+-green.svg)
![React](https://img.shields.io/badge/React-17.0.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**A modern, secure chat application with end-to-end encryption, real-time messaging, and self-destructing messages.**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Security](#-security)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Architecture](#-architecture)
- [Development](#-development)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

Crypt-Talk is a full-stack secure chat application built with Flask (Python) and React. It provides end-to-end encrypted messaging, file sharing with encryption, voice messages, and optional self-destruct timers for sensitive conversations. All communications are encrypted using industry-standard cryptographic algorithms.

**Live Demo:** *(Coming soon)*

---

## ✨ Features

### 🔒 Security Features
- **Message Encryption**: Fernet (AES-128 + HMAC-SHA256) for all text messages
- **File Encryption**: Separate encrypted file sharing with metadata preservation
- **Password Security**: bcrypt hashing with per-password salt generation
- **Integrity Verification**: Message hash validation to prevent tampering
- **Authenticated Encryption**: Built-in authentication tags prevent modifications
- **Secure Key Derivation**: SHA-256 based key generation from user pairs

### 💬 Communication Features
- **Real-Time Messaging**: Socket.IO for instant message delivery
- **File Sharing**: Upload and share encrypted PDFs and images (up to 10MB)
- **Voice Messages**: Record and send voice notes with encryption
- **Message History**: Persistent encrypted message storage
- **Online Status**: Real-time user presence indicators
- **Typing Indicators**: See when others are typing (optional)

### 🎯 Advanced Features
- **Self-Destruct Timers**: Automatic conversation and file deletion
- **Avatar System**: Customizable user avatars
- **Responsive Design**: Mobile and desktop optimized UI
- **Message Receipts**: Delivery and read status
- **File Preview**: Image preview in chat
- **Error Recovery**: Graceful fallbacks for encryption/decryption failures

---

## 🛠 Tech Stack

### Backend
- **Framework**: Flask 2.3.3
- **Database**: MongoDB (PyMongo 4.5.0)
- **Real-Time**: Flask-SocketIO 5.3.6
- **Encryption**: cryptography 41.0.7 (Fernet, AES)
- **Password Hashing**: bcrypt 4.0.1
- **API**: RESTful endpoints with JSON

### Frontend
- **Framework**: React 17.0.2
- **Routing**: React Router DOM 6.2.1
- **Styling**: Styled Components 5.3.3
- **HTTP Client**: Axios 0.28.1
- **Real-Time**: Socket.IO Client 4.4.1
- **UI Components**: React Icons, Emoji Picker, Multiavatar

### DevOps
- **Containerization**: Docker
- **Environment**: python-dotenv for config management
- **CORS**: Flask-CORS for cross-origin requests

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Node.js 14.x or higher
- MongoDB 4.x or higher
- Git

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/crypt-talk.git
cd crypt-talk
```

#### 2. Setup Backend
```bash
cd server

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "MONGO_URL=mongodb://localhost:27017/crypttalk" > .env
echo "PORT=5000" >> .env
echo "FLASK_ENV=development" >> .env

# Run server
python app.py
```

#### 3. Setup Frontend
```bash
cd public

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_LOCALHOST_KEY=chat-app-current-user" > .env
echo "REACT_APP_API_URL=http://localhost:5000" >> .env

# Run development server
npm start
```

#### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Test User**: username=`testuser`, password=`password123`

---

## 📁 Project Structure

```
crypt-talk/
├── server/                          # Backend (Python/Flask)
│   ├── app.py                       # Main Flask application
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Docker configuration
│   ├── .env                         # Environment variables
│   │
│   ├── communication/               # Core communication modules
│   │   ├── __init__.py
│   │   │
│   │   ├── encryption/             # Message encryption
│   │   │   ├── __init__.py
│   │   │   └── message_encryption.py
│   │   │
│   │   ├── file_sharing/           # File handling & encryption
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py
│   │   │   └── file_encryption.py
│   │   │
│   │   ├── messaging/              # Message management
│   │   │   ├── __init__.py
│   │   │   └── message_handler.py
│   │   │
│   │   ├── socketio/               # Real-time communication
│   │   │   ├── __init__.py
│   │   │   └── socket_handler.py
│   │   │
│   │   ├── self_destruct/          # Auto-deletion
│   │   │   ├── __init__.py
│   │   │   └── timer_handler.py
│   │   │
│   │   └── voice_messages/         # Voice handling
│   │       ├── __init__.py
│   │       └── voice_handler.py
│   │
│   └── voice_uploads/              # Voice file storage
│
├── public/                          # Frontend (React)
│   ├── package.json                # Node dependencies
│   ├── .env                        # Environment variables
│   │
│   ├── public/                     # Static assets
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   └── src/
│       ├── App.js                  # Main React component
│       ├── index.js                # Entry point
│       ├── index.css               # Global styles
│       │
│       ├── assets/                 # Images & media
│       │   ├── logo.svg
│       │   ├── loader.gif
│       │   └── robot.gif
│       │
│       ├── components/             # Reusable components
│       │   ├── ChatContainer.jsx   # Main chat interface
│       │   ├── ChatInput.jsx       # Message input
│       │   ├── Contacts.jsx        # User list
│       │   ├── Welcome.jsx         # Welcome screen
│       │   ├── Logout.jsx          # Logout button
│       │   ├── SetAvatar.jsx       # Avatar selection
│       │   ├── VoiceRecorder.jsx   # Voice recording
│       │   ├── VoiceMessage.jsx    # Voice playback
│       │   ├── ImagePreview.jsx    # Image preview
│       │   └── SelfDestructTimer.jsx
│       │
│       ├── pages/                  # Page components
│       │   ├── Chat.jsx            # Main chat page
│       │   ├── Login.jsx           # Login page
│       │   └── Register.jsx        # Registration page
│       │
│       └── utils/                  # Utilities
│           ├── APIRoutes.js        # API endpoints
│           └── clientEncryption.js # Client-side crypto
│
├── docs/                           # Documentation
│   ├── API.md                      # API documentation
│   ├── ARCHITECTURE.md             # System architecture
│   ├── DEPLOYMENT.md               # Deployment guide
│   └── SECURITY.md                 # Security details
│
├── README.md                       # This file
└── working.txt                     # Technical notes
```

---

## ⚙️ Configuration

### Backend Environment Variables (.env)
```env
# MongoDB connection string
MONGO_URL=mongodb://localhost:27017/crypttalk

# Server port
PORT=5000

# Environment (development/production)
FLASK_ENV=development

# Enable verbose crypto logging (optional)
CRYPTO_VERBOSE=false
```

### Frontend Environment Variables (.env)
```env
# LocalStorage key for user session
REACT_APP_LOCALHOST_KEY=chat-app-current-user

# Backend API URL
REACT_APP_API_URL=http://localhost:5000
```

---

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string"
}

Response: 200 OK
{
  "status": true,
  "user": {
    "_id": "string",
    "username": "string",
    "email": "string",
    "isAvatarImageSet": false,
    "avatarImage": ""
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response: 200 OK
{
  "status": true,
  "user": { /* user object */ }
}
```

#### Set Avatar
```http
POST /api/auth/setavatar/:userId
Content-Type: application/json

{
  "image": "base64_image_string"
}
```

#### Get All Users
```http
GET /api/auth/allusers/:userId

Response: 200 OK
[
  {
    "_id": "string",
    "username": "string",
    "email": "string",
    "avatarImage": "string"
  }
]
```

### Messaging Endpoints

#### Send Message
```http
POST /api/messages/addmsg
Content-Type: application/json

{
  "from": "userId",
  "to": "userId",
  "message": "string"
}
```

#### Get Messages
```http
POST /api/messages/getmsg
Content-Type: application/json

{
  "from": "userId",
  "to": "userId"
}

Response: 200 OK
[
  {
    "fromSelf": boolean,
    "type": "text",
    "message": "string"
  }
]
```

### File Sharing Endpoints

#### Upload File
```http
POST /api/files/upload
Content-Type: multipart/form-data

file: File
from: userId
to: userId

Response: 200 OK
{
  "status": true,
  "file_id": "string",
  "filename": "string"
}
```

#### Download File
```http
GET /api/files/download/:fileId

Response: 200 OK
Content-Type: application/pdf | image/*
Content-Disposition: attachment; filename="..."
```

### Socket.IO Events

#### Client → Server
- `add-user` - Register user online
- `send-msg` - Send real-time message
- `send-file` - Send file notification
- `send-voice` - Send voice message

#### Server → Client
- `msg-recieve` - Receive message
- `file-recieve` - Receive file notification
- `voice-recieve` - Receive voice message
- `user-connected` - User came online
- `user-disconnected` - User went offline

**For complete API documentation, see [docs/API.md](docs/API.md)**

---

## 🔐 Security

### Encryption Algorithms

#### Message Encryption
- **Algorithm**: Fernet (AES-128-CBC + HMAC-SHA256)
- **Key Derivation**: SHA-256 hash from sorted user IDs
- **Key Format**: Base64-encoded 32-byte key
- **Features**: Authenticated encryption, timestamp validation

#### Password Security
- **Algorithm**: bcrypt with per-password salt
- **Work Factor**: Default bcrypt cost (currently 12)
- **Timing Attack Protection**: Built-in constant-time comparison

#### File Encryption
- **Algorithm**: Fernet (same as messages)
- **Key Namespace**: Separate "FILE:" prefix for isolation
- **Metadata**: Preserved for images (EXIF data)
- **Integrity**: Hash validation on decryption

### Security Best Practices

✅ **Implemented**
- Password hashing with bcrypt
- End-to-end message encryption
- Encrypted file storage
- Input validation and sanitization
- File type and size restrictions
- Secure filename generation
- CORS configuration
- Error handling without information leakage

⚠️ **Production Requirements**
- HTTPS/TLS for all traffic (required)
- WebSocket Secure (WSS) for Socket.IO
- MongoDB authentication and authorization
- Rate limiting for API endpoints
- Session management with secure cookies
- Regular security audits and updates
- Key rotation policies
- Backup encryption

**For detailed security information, see [docs/SECURITY.md](docs/SECURITY.md)**

---

## 🏗 Architecture

### System Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Browser   │◄───────►│ Flask Server│◄───────►│   MongoDB   │
│  (React)    │  HTTP   │  + SocketIO │  PyMongo│  Database   │
└─────────────┘ WebSocket└─────────────┘         └─────────────┘
      │                        │
      │                        │
      ▼                        ▼
 ┌─────────┐            ┌─────────────┐
 │ Local   │            │ File System │
 │ Storage │            │ (uploads/)  │
 └─────────┘            └─────────────┘
```

### Data Flow

#### Message Flow
1. User types message in React UI
2. Client sends via Socket.IO (real-time) and HTTP (persistence)
3. Server encrypts message with Fernet
4. Encrypted message stored in MongoDB
5. Server emits to recipient via Socket.IO
6. Recipient receives and displays message
7. Message history retrieved and decrypted on demand

#### File Flow
1. User selects file in React UI
2. Client uploads via multipart form data
3. Server validates and encrypts file
4. Encrypted file saved to disk + metadata to MongoDB
5. File message created and emitted
6. Recipient downloads and server decrypts on-the-fly

**For detailed architecture, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

---

## 💻 Development

### Running Tests
```bash
# Backend tests (coming soon)
cd server
pytest

# Frontend tests
cd public
npm test
```

### Development Mode

#### Backend with Hot Reload
```bash
cd server
export FLASK_ENV=development
python app.py
```

#### Frontend with Fast Refresh
```bash
cd public
npm start
```

### Code Style

#### Python (Backend)
- Follow PEP 8 style guide
- Use docstrings for all modules and functions
- Type hints recommended

#### JavaScript (Frontend)
- ESLint configuration in package.json
- React functional components preferred
- Styled-components for CSS

### Debugging

#### Enable Verbose Logging
```bash
# Backend
export CRYPTO_VERBOSE=true
python app.py

# Frontend
# Open browser DevTools Console
```

---

## 🚢 Deployment

### Render + Vercel Deployment (Recommended)

Deploy your backend to **Render** (free tier) and frontend to **Vercel** (free tier) in minutes!

---

### Part 1: Backend Deployment (Render)

#### Step 1: Setup MongoDB Atlas
```bash
1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create a free M0 cluster (512MB storage)
3. Database Access → Create user with password
4. Network Access → Add IP: 0.0.0.0/0 (allow all)
5. Get connection string:
   mongodb+srv://<username>:<password>@cluster.mongodb.net/crypttalk
```

#### Step 2: Deploy Backend to Render

**Option A: Deploy from GitHub (Recommended)**
```bash
1. Push your code to GitHub
2. Go to https://render.com and sign in
3. Dashboard → "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - Name: crypt-talk-backend
   - Region: Oregon (US West)
   - Branch: main
   - Root Directory: server
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: python app.py
6. Click "Create Web Service"
```

**Option B: Manual Git Deployment**
```bash
# From server folder
cd server

# Initialize git if needed
git init
git add .
git commit -m "Initial commit"

# Deploy to Render (follow dashboard prompts)
```

#### Step 3: Configure Render Environment Variables
```bash
In Render Dashboard → Your Service → Environment:

Add these variables:
┌─────────────────────┬────────────────────────────────────────────┐
│ Key                 │ Value                                      │
├─────────────────────┼────────────────────────────────────────────┤
│ MONGO_URL           │ mongodb+srv://user:pass@cluster.mongodb... │
│ FLASK_ENV           │ production                                 │
│ PORT                │ 5000                                       │
│ PYTHONUNBUFFERED    │ 1                                          │
└─────────────────────┴────────────────────────────────────────────┘

Save → Render will auto-deploy with new variables
```

#### Step 4: Get Your Backend URL
```bash
1. Wait for deployment to complete (~2-3 minutes)
2. Copy your URL: https://crypt-talk-backend.onrender.com
3. Test: https://your-app.onrender.com/api/auth/allusers/test
```

---

### Part 2: Frontend Deployment (Vercel)

#### Step 1: Update Frontend Environment
```bash
# In public/.env file
REACT_APP_API_URL=https://crypt-talk-backend.onrender.com
REACT_APP_LOCALHOST_KEY=chat-app-current-user
```

#### Step 2: Deploy to Vercel

**Option A: Vercel CLI (Fastest)**
```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend
cd public

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? crypt-talk
# - In which directory is your code? ./
# - Override settings? No

# Production deployment
vercel --prod
```

**Option B: Vercel Dashboard**
```bash
1. Go to https://vercel.com and sign in
2. "New Project" → Import your GitHub repo
3. Configure:
   - Framework Preset: Create React App
   - Root Directory: public
   - Build Command: npm run build
   - Output Directory: build
4. Environment Variables → Add:
   - REACT_APP_API_URL: https://your-backend.onrender.com
   - REACT_APP_LOCALHOST_KEY: chat-app-current-user
5. Click "Deploy"
```

#### Step 3: Access Your Live App
```bash
Your app is live at: https://crypt-talk.vercel.app
Backend API: https://crypt-talk-backend.onrender.com
```

---

### Important: Update Backend CORS

After deploying frontend, update [server/app.py](server/app.py):

```python
# Replace CORS configuration
CORS(app, 
     resources={r"/*": {
         "origins": [
             "https://crypt-talk.vercel.app",  # Your Vercel domain
             "http://localhost:3000"            # Local development
         ],
         "supports_credentials": True
     }})

# Update Socket.IO CORS
socketio = SocketIO(app, 
                   cors_allowed_origins=[
                       "https://crypt-talk.vercel.app",
                       "http://localhost:3000"
                   ])
```

Redeploy backend on Render after this change.

---

### Docker Deployment (Alternative)

#### Build and Run
```bash
# Backend
cd server
docker build -t crypt-talk-backend .
docker run -p 5000:5000 --env-file .env crypt-talk-backend

# Frontend
cd public
docker build -t crypt-talk-frontend .
docker run -p 3000:3000 crypt-talk-frontend
```

---

### Production Checklist

**Backend (Render):**
- [x] HTTPS/TLS (automatic on Render)
- [x] WSS for Socket.IO (automatic with HTTPS)
- [x] MongoDB Atlas with authentication
- [x] Environment variables configured
- [ ] Update CORS to specific frontend domain
- [ ] Add rate limiting middleware
- [ ] Set up health checks
- [ ] Monitor logs in Render dashboard

**Frontend (Vercel):**
- [x] HTTPS (automatic on Vercel)
- [x] CDN distribution (automatic)
- [x] Environment variables set
- [ ] Custom domain (optional)
- [ ] Enable analytics (optional)

---

### Troubleshooting

#### Issue: Render Build Fails
```bash
# Check Render logs in dashboard
# Common fixes:
1. Ensure requirements.txt includes all dependencies
2. Verify Python version (3.11 specified in render.yaml)
3. Check for syntax errors in app.py
```

#### Issue: Frontend Can't Connect to Backend
```bash
# Verify:
1. REACT_APP_API_URL matches Render backend URL
2. CORS is configured in app.py
3. Backend is running (check Render dashboard)
4. Rebuild frontend: npm run build && vercel --prod
```

#### Issue: Socket.IO Connection Failed
```bash
# Ensure:
1. Backend uses wss:// (automatic with HTTPS)
2. CORS origins include your Vercel domain
3. No firewall blocking WebSocket connections
```

#### Issue: Render Free Tier Sleeps
```bash
# Render free tier sleeps after 15 minutes of inactivity
# First request after sleep takes ~30 seconds
# Solutions:
1. Upgrade to paid tier ($7/month)
2. Use cron job to ping every 10 minutes
3. Add loading message for cold starts
```

---

### Cost Breakdown

| Service | Plan | Cost | Limits |
|---------|------|------|--------|
| Render | Free | $0 | 750 hrs/month, sleeps after 15min |
| Vercel | Hobby | $0 | 100GB bandwidth/month |
| MongoDB Atlas | M0 | $0 | 512MB storage, shared cluster |
| **Total** | | **$0/month** | Perfect for portfolio projects |

**For complete deployment guide, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Follow existing code style
- Ensure all tests pass before submitting

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Frontend powered by [React](https://reactjs.org/)
- Encryption using [cryptography](https://cryptography.io/)
- Real-time with [Socket.IO](https://socket.io/)
- Icons from [React Icons](https://react-icons.github.io/react-icons/)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/crypt-talk/issues)
- **Email**: support@crypt-talk.com
- **Discord**: [Join our server](https://discord.gg/crypttalk)

---

<div align="center">

**Made with ❤️ and 🔐 by the Crypt-Talk Team**

[⬆ back to top](#-crypt-talk---secure-real-time-chat-application)

</div>