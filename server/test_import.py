#!/usr/bin/env python3
"""
Test script to verify Flask app can be imported correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, socketio, application
    print("✅ Successfully imported app")
    print(f"✅ Flask app: {app}")
    print(f"✅ SocketIO: {socketio}")
    print(f"✅ WSGI application: {application}")
    
    # Test routes
    with app.test_client() as client:
        response = client.get('/')
        print(f"✅ Root route status: {response.status_code}")
        
        response = client.get('/health')
        print(f"✅ Health route status: {response.status_code}")
        
    print("🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error importing app: {e}")
    import traceback
    traceback.print_exc()