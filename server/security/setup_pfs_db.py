"""
🔧 MongoDB PFS Session Setup
=============================

This script sets up the MongoDB collection for PFS session storage.
Run this once to create the required indexes and schema.
"""

from pymongo import MongoClient, ASCENDING
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_pfs_collection():
    """
    Create PFS sessions collection with proper indexes
    """
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/crypt_talk')
    client = MongoClient(mongo_url)
    db = client.get_database()
    
    print("🔗 Connected to MongoDB")
    print(f"📊 Database: {db.name}")
    
    # Create pfs_sessions collection if doesn't exist
    if 'pfs_sessions' not in db.list_collection_names():
        db.create_collection('pfs_sessions')
        print("✅ Created 'pfs_sessions' collection")
    else:
        print("ℹ️  'pfs_sessions' collection already exists")
    
    pfs_collection = db.pfs_sessions
    
    # Create indexes for fast lookups
    indexes_to_create = [
        {
            'keys': [('conversation_id', ASCENDING)],
            'unique': True,
            'name': 'conversation_id_unique'
        },
        {
            'keys': [('user1_id', ASCENDING), ('user2_id', ASCENDING)],
            'name': 'users_compound_index'
        },
        {
            'keys': [('updated_at', ASCENDING)],
            'name': 'updated_at_index'
        }
    ]
    
    print("\n📑 Creating indexes...")
    for index_spec in indexes_to_create:
        try:
            pfs_collection.create_index(
                index_spec['keys'],
                unique=index_spec.get('unique', False),
                name=index_spec['name']
            )
            print(f"  ✅ Index '{index_spec['name']}' created")
        except Exception as e:
            print(f"  ⚠️  Index '{index_spec['name']}' already exists or error: {e}")
    
    # Add sample document structure (for documentation)
    sample_doc = {
        "_id": "example_only_delete_me",
        "conversation_id": "user1_id-user2_id",
        "user1_id": "user1_id",
        "user2_id": "user2_id",
        "session_state": {
            "root_key": "<hex_encoded_root_key>",
            "chain_keys": {
                "sending": "<hex_encoded_sending_chain_key>",
                "receiving": "<hex_encoded_receiving_chain_key>"
            },
            "ratchet_keys": {
                "private": "<hex_encoded_private_key>",
                "public": "<hex_encoded_public_key>",
                "remote_public": "<hex_encoded_remote_public_key>"
            },
            "counters": {
                "sending": 0,
                "receiving": 0,
                "previous_sending": 0
            },
            "skipped_message_keys": {}
        },
        "created_at": int(datetime.now().timestamp()),
        "updated_at": int(datetime.now().timestamp())
    }
    
    # Insert sample if collection is empty
    if pfs_collection.count_documents({}) == 0:
        pfs_collection.insert_one(sample_doc)
        print("\n📝 Inserted sample document structure")
        print("   (Delete with: db.pfs_sessions.deleteOne({_id: 'example_only_delete_me'}))")
    
    # Add validation schema
    try:
        db.command({
            'collMod': 'pfs_sessions',
            'validator': {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['conversation_id', 'user1_id', 'user2_id', 'updated_at'],
                    'properties': {
                        'conversation_id': {
                            'bsonType': 'string',
                            'description': 'Unique conversation identifier'
                        },
                        'user1_id': {
                            'bsonType': 'string',
                            'description': 'First user ID'
                        },
                        'user2_id': {
                            'bsonType': 'string',
                            'description': 'Second user ID'
                        },
                        'session_state': {
                            'bsonType': 'object',
                            'description': 'PFS ratchet state'
                        },
                        'created_at': {
                            'bsonType': 'int',
                            'description': 'Session creation timestamp'
                        },
                        'updated_at': {
                            'bsonType': 'int',
                            'description': 'Last update timestamp'
                        }
                    }
                }
            },
            'validationLevel': 'moderate'
        })
        print("\n✅ Schema validation added")
    except Exception as e:
        print(f"\n⚠️  Schema validation: {e}")
    
    # Print collection stats
    stats = pfs_collection.estimated_document_count()
    print(f"\n📈 Collection Stats:")
    print(f"   Documents: {stats}")
    print(f"   Indexes: {len(list(pfs_collection.list_indexes()))}")
    
    print("\n✅ PFS session storage setup complete!")
    print("\n📚 Usage:")
    print("   - PFS sessions auto-created when users start chatting")
    print("   - Session state saved after every message")
    print("   - Old sessions can be cleaned up with TTL index (optional)")
    
    client.close()
    print("\n🔌 MongoDB connection closed")

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 PFS SESSION STORAGE SETUP")
    print("=" * 60)
    print()
    
    try:
        setup_pfs_collection()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure:")
        print("   1. MongoDB is running")
        print("   2. MONGO_URL in .env is correct")
        print("   3. Database has write permissions")
