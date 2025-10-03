# Multi-stage build for React + Flask
FROM node:18-alpine as frontend-build

# Build React frontend
WORKDIR /app/public
COPY public/package*.json ./
RUN npm install
COPY public/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

# Install Python dependencies
WORKDIR /app
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy server files
COPY server/ ./

# Copy built frontend
COPY --from=frontend-build /app/public/build ./static

# Expose port
EXPOSE $PORT

# Start the application
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT"]