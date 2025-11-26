#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Setup MongoDB collections cho CityLens
Collections:
- events: Real-time events (report created, status changed, etc.)
- analytics: Daily/hourly aggregated statistics
- notifications: User notifications queue
- websocket_sessions: Active WebSocket connections

Chạy: python scripts/setup_mongodb.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid
from datetime import datetime

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "citylens")


def setup_collections():
    """Create collections with indexes"""
    client = MongoClient(MONGODB_URL)
    db = client[MONGODB_DB]
    
    print(f"📦 Setting up MongoDB: {MONGODB_DB}\n")
    
    # =============================
    # 1. Events Collection
    # =============================
    try:
        db.create_collection("events")
        print("✓ Created collection: events")
    except CollectionInvalid:
        print("- Collection already exists: events")
    
    events = db.events
    
    # Indexes
    events.create_index([("event_type", ASCENDING)])
    events.create_index([("created_at", DESCENDING)])
    events.create_index([("report_id", ASCENDING)])
    events.create_index([("user_id", ASCENDING)])
    events.create_index([("district_id", ASCENDING)])
    
    # TTL index - auto-delete after 30 days
    events.create_index([("created_at", DESCENDING)], expireAfterSeconds=30*24*60*60)
    
    print("  - Indexes: event_type, created_at, report_id, user_id, district_id")
    print("  - TTL: 30 days")
    
    # Sample document
    sample_event = {
        "event_type": "report_created",
        "report_id": 1,
        "user_id": 3,
        "district_id": 1,
        "category": "giao_thong",
        "priority": "high",
        "location": {"lat": 21.0285, "lon": 105.8542},
        "data": {
            "title": "Đường Lê Lợi có ổ gà lớn",
            "status": "pending"
        },
        "created_at": datetime.utcnow()
    }
    
    # =============================
    # 2. Analytics Collection
    # =============================
    try:
        db.create_collection("analytics")
        print("\n✓ Created collection: analytics")
    except CollectionInvalid:
        print("\n- Collection already exists: analytics")
    
    analytics = db.analytics
    
    # Indexes
    analytics.create_index([("type", ASCENDING), ("date", DESCENDING)])
    analytics.create_index([("district_id", ASCENDING), ("date", DESCENDING)])
    
    print("  - Indexes: type+date, district_id+date")
    
    # Sample document
    sample_analytics = {
        "type": "daily_reports",
        "date": "2025-01-15",
        "district_id": 1,
        "metrics": {
            "total_reports": 45,
            "by_category": {
                "giao_thong": 20,
                "moi_truong": 15,
                "ha_tang": 10
            },
            "by_status": {
                "pending": 25,
                "verified": 15,
                "resolved": 5
            },
            "avg_response_time_hours": 12.5
        },
        "created_at": datetime.utcnow()
    }
    
    # =============================
    # 3. Notifications Collection
    # =============================
    try:
        db.create_collection("notifications")
        print("\n✓ Created collection: notifications")
    except CollectionInvalid:
        print("\n- Collection already exists: notifications")
    
    notifications = db.notifications
    
    # Indexes
    notifications.create_index([("user_id", ASCENDING), ("read", ASCENDING)])
    notifications.create_index([("created_at", DESCENDING)])
    
    print("  - Indexes: user_id+read, created_at")
    
    # Sample document
    sample_notification = {
        "user_id": 3,
        "type": "report_status_changed",
        "title": "Báo cáo của bạn đã được xác nhận",
        "message": "Báo cáo 'Đường Lê Lợi có ổ gà lớn' đã được xác nhận bởi moderator",
        "data": {
            "report_id": 1,
            "old_status": "pending",
            "new_status": "verified"
        },
        "read": False,
        "created_at": datetime.utcnow()
    }
    
    # =============================
    # 4. WebSocket Sessions
    # =============================
    try:
        db.create_collection("websocket_sessions")
        print("\n✓ Created collection: websocket_sessions")
    except CollectionInvalid:
        print("\n- Collection already exists: websocket_sessions")
    
    sessions = db.websocket_sessions
    
    # Indexes
    sessions.create_index([("user_id", ASCENDING)])
    sessions.create_index([("connected_at", DESCENDING)])
    
    # TTL index - auto-delete after 1 hour of inactivity
    sessions.create_index([("last_ping", DESCENDING)], expireAfterSeconds=60*60)
    
    print("  - Indexes: user_id, connected_at")
    print("  - TTL: 1 hour")
    
    # Sample document
    sample_session = {
        "session_id": "ws-12345",
        "user_id": 3,
        "socket_id": "abc123",
        "connected_at": datetime.utcnow(),
        "last_ping": datetime.utcnow(),
        "metadata": {
            "ip": "192.168.1.1",
            "user_agent": "Mozilla/5.0..."
        }
    }
    
    print("\n✅ MongoDB setup completed!")
    print(f"   Database: {MONGODB_DB}")
    print(f"   Collections: events, analytics, notifications, websocket_sessions")
    
    # Insert samples (optional)
    if events.count_documents({}) == 0:
        print("\n📝 Inserting sample documents...")
        events.insert_one(sample_event)
        analytics.insert_one(sample_analytics)
        notifications.insert_one(sample_notification)
        sessions.insert_one(sample_session)
        print("✓ Sample documents inserted")
    
    client.close()


def show_stats():
    """Show collection stats"""
    client = MongoClient(MONGODB_URL)
    db = client[MONGODB_DB]
    
    print("\n📊 Collection Stats:")
    for coll_name in ["events", "analytics", "notifications", "websocket_sessions"]:
        count = db[coll_name].count_documents({})
        indexes = len(db[coll_name].list_indexes())
        print(f"   {coll_name}: {count} documents, {indexes} indexes")
    
    client.close()


if __name__ == "__main__":
    try:
        setup_collections()
        show_stats()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure MongoDB is running:")
        print("   brew services start mongodb-community  # macOS")
        print("   sudo systemctl start mongod  # Ubuntu")
        print("   docker run -d -p 27017:27017 mongo:7  # Docker")
