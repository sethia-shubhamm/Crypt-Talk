# Deployment Guide - Vercel (Frontend) + Railway (Backend)

## Prerequisites
- GitHub account
- Vercel account (https://vercel.com/)
- Railway account (https://railway.app/)
- MongoDB Atlas database (already configured)

## Backend Deployment (Railway)

### Step 1: Prepare Repository
1. Push your code to GitHub if not already done:
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

### Step 2: Deploy to Railway
1. Go to https://railway.app/ and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect it's a Python project
5. Click "Deploy Now"

### Step 3: Configure Environment Variables
1. In your Railway project dashboard, go to "Variables" tab
2. Add the following environment variables:
   ```
   MONGO_URL=your_mongodb_atlas_connection_string
   PORT=5000
   CRYPTO_VERBOSE=false
   ```
3. Replace `your_mongodb_atlas_connection_string` with your actual MongoDB connection string

### Step 4: Configure Domain
1. In Railway dashboard, go to "Settings" → "Domains"
2. Generate a domain or add a custom domain
3. Note down the Railway URL (e.g., `https://your-app-name.up.railway.app`)

## Frontend Deployment (Vercel)

### Step 1: Create Environment File
1. In the `public` folder, create a `.env` file:
   ```
   REACT_APP_API_URL=https://your-railway-url.up.railway.app
   ```
   Replace with your actual Railway URL from Step 4 above

### Step 2: Deploy to Vercel
1. Go to https://vercel.com/ and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Select the `public` folder as the root directory
5. Add environment variable:
   - Key: `REACT_APP_API_URL`
   - Value: Your Railway backend URL (e.g., `https://your-app-name.up.railway.app`)
6. Click "Deploy"

### Step 3: Configure Domain (Optional)
1. In Vercel dashboard, go to "Settings" → "Domains"
2. Add a custom domain if desired

## Final Configuration

### Update CORS in Backend (if needed)
If you encounter CORS issues, update your Flask app to allow your Vercel domain:

1. In `server/app.py`, update the CORS configuration:
   ```python
   from flask_cors import CORS
   
   # Update CORS to include your Vercel domain
   CORS(app, origins=["https://your-vercel-app.vercel.app", "http://localhost:3000"])
   ```

### Test Your Deployment
1. Visit your Vercel frontend URL
2. Register a new account
3. Test messaging functionality
4. Test file sharing
5. Test real-time communication

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Make sure your backend CORS configuration includes your Vercel domain

2. **WebSocket Connection Failed**: Ensure your Railway backend supports WebSocket connections (it should with our eventlet configuration)

3. **Environment Variables**: Double-check that:
   - Railway has `MONGO_URL`, `PORT`, and `CRYPTO_VERBOSE` set
   - Vercel has `REACT_APP_API_URL` set to your Railway URL

4. **Build Errors**: Make sure all dependencies are listed in requirements.txt (backend) and package.json (frontend)

### Logs:
- Railway logs: Go to your Railway project → "Deployments" → Click on latest deployment
- Vercel logs: Go to your Vercel project → "Functions" tab

## Security Notes
- Never commit `.env` files to version control
- Use environment variables for all sensitive data
- Your MongoDB connection string should only be in Railway environment variables
- The frontend only needs the `REACT_APP_API_URL` environment variable

## Scaling
- Railway automatically scales based on usage
- Vercel automatically handles CDN and global distribution
- Monitor usage in both platforms' dashboards

Your chat application should now be fully deployed and accessible worldwide! 🚀