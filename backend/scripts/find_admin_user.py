#!/usr/bin/env python3
"""
Find the correct user ID for vitalijs@axwise.de
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.models import User

# Production database URL
PRODUCTION_DATABASE_URL=***REDACTED***

# Create production database session
engine = create_engine(PRODUCTION_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def find_admin_user():
    """Find the admin user by email."""
    
    admin_email = "vitalijs@axwise.de"
    
    print(f"🔍 Looking for admin user: {admin_email}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Find the user by email
        user = db.query(User).filter(User.email == admin_email).first()
        
        if not user:
            print(f"❌ User with email {admin_email} not found!")
            
            # Let's see all users to understand what's in the database
            print("\n📋 All users in database:")
            all_users = db.query(User).all()
            for u in all_users:
                print(f"   - ID: {u.user_id}, Email: {u.email}, Status: {u.subscription_status}")
            return
        
        print(f"✅ Found admin user:")
        print(f"   - User ID: {user.user_id}")
        print(f"   - Email: {user.email}")
        print(f"   - Subscription Status: {user.subscription_status}")
        print(f"   - Subscription ID: {user.subscription_id}")
        print(f"   - Usage Data: {user.usage_data}")
        
        return user.user_id
        
    except Exception as e:
        print(f"❌ Error finding admin user: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    find_admin_user()
