#!/usr/bin/env python3
"""
Debug usage data for iforgez@gmail.com user
"""

import sys
import os
from datetime import datetime, timezone
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

def debug_iforgez_user():
    """Debug the iforgez@gmail.com user's usage data."""
    
    target_email = "iforgez@gmail.com"
    
    print(f"🔍 Debugging usage data for user: {target_email}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Find the user by email
        user = db.query(User).filter(User.email == target_email).first()
        
        if not user:
            print(f"❌ User {target_email} not found!")
            return
        
        print(f"✅ Found user: {user.email}")
        print(f"📊 User ID: {user.user_id}")
        print(f"📊 Current subscription_status: {user.subscription_status}")
        print(f"📊 Current subscription_id: {user.subscription_id}")
        
        # Get current month
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        print(f"📅 Current month: {current_month}")
        
        # Debug usage_data structure
        print(f"\n📋 Full usage_data:")
        import json
        print(json.dumps(user.usage_data, indent=2))
        
        # Check if usage_data exists and has the right structure
        if not user.usage_data:
            print("❌ No usage_data found!")
            return
            
        if "usage" not in user.usage_data:
            print("❌ No 'usage' key in usage_data!")
            return
            
        print(f"\n📊 Available months in usage data:")
        for month in user.usage_data["usage"].keys():
            month_data = user.usage_data["usage"][month]
            print(f"   - {month}: {month_data.get('analyses_count', 0)} analyses, {month_data.get('prd_generations_count', 0)} PRDs")
            
        # Check current month specifically
        if current_month in user.usage_data["usage"]:
            current_data = user.usage_data["usage"][current_month]
            print(f"\n✅ Current month ({current_month}) data:")
            print(f"   - Analyses count: {current_data.get('analyses_count', 0)}")
            print(f"   - PRD count: {current_data.get('prd_generations_count', 0)}")
            print(f"   - Analyses list: {current_data.get('analyses', [])}")
        else:
            print(f"\n❌ No data for current month ({current_month})")
            
        # Check subscription data
        if "subscription" in user.usage_data:
            sub_data = user.usage_data["subscription"]
            print(f"\n📋 Subscription data:")
            print(f"   - Tier: {sub_data.get('tier', 'N/A')}")
            print(f"   - Status: {sub_data.get('status', 'N/A')}")
            print(f"   - Trial end: {sub_data.get('trial_end', 'N/A')}")
        else:
            print(f"\n❌ No subscription data in usage_data")
            
        # Check what the backend would calculate for limits
        print(f"\n🧮 Expected backend calculation:")
        if user.subscription_status == "trialing":
            print(f"   - Expected tier: pro (because status is trialing)")
            print(f"   - Expected limits: 100 analyses/month")
        else:
            print(f"   - Expected tier: free (no active subscription)")
            print(f"   - Expected limits: 3 analyses/month")
        
    except Exception as e:
        print(f"❌ Error debugging usage data: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    debug_iforgez_user()
