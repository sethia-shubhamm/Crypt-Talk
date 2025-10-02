# Python Flask Backend

MongoDB-powered backend for the Crypt-Talk application.

## Prerequisites

- MongoDB Atlas account and connection string
- Python 3.9+

## Quick Start

1. **Set up MongoDB Atlas** (see ATLAS_SETUP_GUIDE.md)

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
   Update `.env` with your MongoDB Atlas connection string:
   ```
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/crypt-talk
   PORT=5000
   ```

4. **Run the application**:
```bash
python app.py
```

The server starts on `http://localhost:5000` with:
- ✅ MongoDB Atlas connection
- 👤 Test user: `testuser` / `password123`

## API Endpoints

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/logout/<user_id>` - Logout user
- `GET /api/auth/allusers/<user_id>` - Get all users except current user
- `POST /api/auth/setavatar/<user_id>` - Set user avatar

## Database

- **Database**: MongoDB Atlas (cloud)
- **Collections**: `users`
- **Features**: Persistent storage, automatic backups, scalable