#!/usr/bin/env python3
"""
Debug ihomezy@gmail.com user for checkout failure investigation
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

def debug_ihomezy_user():
    """Debug the ihomezy@gmail.com user's data."""
    
    target_email = "ihomezy@gmail.com"
    
    print(f"🔍 Debugging user for checkout failure: {target_email}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Find the user by email
        user = db.query(User).filter(User.email == target_email).first()
        
        if not user:
            print(f"❌ User {target_email} not found!")
            print("\n📋 All users in database:")
            all_users = db.query(User).all()
            for u in all_users:
                print(f"   - Email: {u.email}, ID: {u.user_id}")
            return
        
        print(f"✅ Found user: {user.email}")
        print(f"📊 User ID: {user.user_id}")
        print(f"📊 First Name: {user.first_name}")
        print(f"📊 Last Name: {user.last_name}")
        print(f"📊 Stripe Customer ID: {user.stripe_customer_id}")
        print(f"📊 Subscription Status: {user.subscription_status}")
        print(f"📊 Subscription ID: {user.subscription_id}")
        
        # Get current month
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        print(f"📅 Current month: {current_month}")
        
        # Debug usage_data structure
        print(f"\n📋 Full usage_data:")
        import json
        if user.usage_data:
            print(json.dumps(user.usage_data, indent=2))
        else:
            print("None")
        
        # Check Stripe customer status
        print(f"\n💳 Stripe Integration Status:")
        if user.stripe_customer_id:
            print(f"   ✅ Has Stripe Customer ID: {user.stripe_customer_id}")
        else:
            print(f"   ❌ No Stripe Customer ID - This could cause checkout failures!")
            
        # Check subscription data consistency
        print(f"\n🔄 Subscription Data Consistency:")
        has_subscription_status = bool(user.subscription_status)
        has_subscription_id = bool(user.subscription_id)
        has_usage_data_subscription = bool(user.usage_data and "subscription" in user.usage_data)
        
        print(f"   - Has subscription_status: {has_subscription_status}")
        print(f"   - Has subscription_id: {has_subscription_id}")
        print(f"   - Has usage_data subscription: {has_usage_data_subscription}")
        
        if has_subscription_status != has_subscription_id:
            print(f"   ⚠️ Inconsistent subscription data!")
            
        # Check what the backend would calculate for limits
        print(f"\n🧮 Expected backend calculation:")
        if user.subscription_status == "trialing":
            print(f"   - Expected tier: pro (because status is trialing)")
            print(f"   - Expected limits: 100 analyses/month")
        elif user.subscription_status in ["active", "past_due"]:
            print(f"   - Expected tier: Based on Stripe subscription")
            print(f"   - Expected limits: Based on subscription tier")
        else:
            print(f"   - Expected tier: free (no active subscription)")
            print(f"   - Expected limits: 3 analyses/month")
            
        # Check for potential checkout issues
        print(f"\n🚨 Potential Checkout Issues:")
        issues = []
        
        if not user.stripe_customer_id:
            issues.append("Missing Stripe Customer ID")
        if user.subscription_status and not user.subscription_id:
            issues.append("Has subscription status but no subscription ID")
        if user.subscription_id and not user.subscription_status:
            issues.append("Has subscription ID but no subscription status")
            
        if issues:
            for issue in issues:
                print(f"   ❌ {issue}")
        else:
            print(f"   ✅ No obvious data issues found")
        
    except Exception as e:
        print(f"❌ Error debugging user: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    debug_ihomezy_user()
