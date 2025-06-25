#!/usr/bin/env python3
"""
List all users in the production database

This script helps identify user IDs for account management.
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

def list_all_users():
    """List all users in the database."""
    
    print("👥 Listing all users in production database")
    print("=" * 60)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        
        if not users:
            print("❌ No users found in database!")
            return
        
        print(f"✅ Found {len(users)} users:")
        print()
        
        for i, user in enumerate(users, 1):
            print(f"{i}. User ID: {user.user_id}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   Subscription Status: {user.subscription_status}")
            print(f"   Subscription ID: {user.subscription_id}")
            print(f"   Stripe Customer ID: {user.stripe_customer_id}")
            
            # Show subscription tier from usage_data
            if user.usage_data and "subscription" in user.usage_data:
                tier = user.usage_data["subscription"].get("tier", "unknown")
                status = user.usage_data["subscription"].get("status", "unknown")
                print(f"   Usage Data Tier: {tier}")
                print(f"   Usage Data Status: {status}")
            else:
                print(f"   Usage Data: No subscription data")
            
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error listing users: {str(e)}")
    finally:
        db.close()

def search_users_by_name(search_term: str):
    """Search for users by name or email."""
    
    print(f"🔍 Searching for users matching: '{search_term}'")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Search by email, first_name, or last_name
        users = db.query(User).filter(
            (User.email.ilike(f"%{search_term}%")) |
            (User.first_name.ilike(f"%{search_term}%")) |
            (User.last_name.ilike(f"%{search_term}%"))
        ).all()
        
        if not users:
            print(f"❌ No users found matching '{search_term}'")
            return
        
        print(f"✅ Found {len(users)} matching users:")
        print()
        
        for i, user in enumerate(users, 1):
            print(f"{i}. User ID: {user.user_id}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   Subscription Status: {user.subscription_status}")
            
            # Show subscription tier from usage_data
            if user.usage_data and "subscription" in user.usage_data:
                tier = user.usage_data["subscription"].get("tier", "unknown")
                status = user.usage_data["subscription"].get("status", "unknown")
                print(f"   Tier: {tier} ({status})")
            
            print("-" * 30)
        
    except Exception as e:
        print(f"❌ Error searching users: {str(e)}")
    finally:
        db.close()

def main():
    """Main function to list or search users."""
    
    if len(sys.argv) > 1:
        # Search mode
        search_term = sys.argv[1]
        search_users_by_name(search_term)
    else:
        # List all users mode
        list_all_users()
    
    print("\n💡 Usage:")
    print("  python backend/scripts/list_users.py                    # List all users")
    print("  python backend/scripts/list_users.py typhanie           # Search for 'typhanie'")
    print("  python backend/scripts/list_users.py andrew             # Search for 'andrew'")

if __name__ == "__main__":
    main()
