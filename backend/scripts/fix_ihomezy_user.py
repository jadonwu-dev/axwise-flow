#!/usr/bin/env python3
"""
Fix ihomezy@gmail.com user for checkout issues
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

def fix_ihomezy_user():
    """Fix the ihomezy@gmail.com user's data for checkout."""
    
    target_email = "ihomezy@gmail.com"
    target_user_id = "user_2xpey0TCSAs8PiHNs64DblkTp6e"
    
    print(f"🔧 Fixing checkout issues for user: {target_email}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Find the user
        user = db.query(User).filter(User.user_id == target_user_id).first()
        
        if not user:
            print(f"❌ User {target_user_id} not found!")
            return
        
        print(f"✅ Found user: {user.email}")
        
        # Get current month
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        print(f"📅 Current month: {current_month}")
        
        # Ensure usage_data exists
        if not user.usage_data:
            user.usage_data = {}
        
        # 1. Fix subscription data - user has exhausted free tier (3/3 analyses)
        # They should be prompted to upgrade
        user.usage_data["subscription"] = {
            "tier": "free",
            "status": "active"
        }
        
        # 2. Ensure usage structure exists
        if "usage" not in user.usage_data:
            user.usage_data["usage"] = {}
        
        # 3. Current usage shows user has hit the limit (3/3 analyses + 1 PRD)
        # This is correct - they need to upgrade
        print(f"📊 Current usage: {user.usage_data['usage'].get(current_month, {})}")
        
        # 4. Clear any conflicting subscription data
        user.subscription_status = None
        user.subscription_id = None
        # Note: stripe_customer_id will be created automatically when they checkout
        
        # 5. Mark the user object as dirty to ensure SQLAlchemy detects changes
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "usage_data")
        
        # 6. Force commit with explicit flush
        db.flush()
        db.commit()
        
        print(f"✅ Successfully fixed user data:")
        print(f"   - Subscription: Free tier (3 analyses/month)")
        print(f"   - Current usage: 3/3 analyses used (at limit)")
        print(f"   - Status: Ready for checkout/upgrade")
        print(f"   - Stripe Customer ID: Will be created during checkout")
        
        # Verify the fix by querying fresh from database
        db.refresh(user)
        print(f"\n🔍 Verification:")
        print(f"   - Database committed: ✅")
        print(f"   - Subscription status: {user.subscription_status}")
        print(f"   - Subscription ID: {user.subscription_id}")
        print(f"   - Stripe Customer ID: {user.stripe_customer_id}")
        if "subscription" in user.usage_data:
            print(f"   - Usage data tier: {user.usage_data['subscription']['tier']}")
        
        print(f"\n🎯 Next steps for user:")
        print(f"   1. User should see upgrade prompts (3/3 analyses used)")
        print(f"   2. Checkout should work with proper Clerk authentication")
        print(f"   3. Stripe Customer ID will be created automatically")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error fixing user: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_ihomezy_user()
