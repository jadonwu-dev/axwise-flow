#!/usr/bin/env python3
"""
Complete fix for iforgez@gmail.com user subscription and usage data
"""

import sys
import os
from datetime import datetime, timedelta, timezone
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

def fix_iforgez_complete():
    """Complete fix for iforgez@gmail.com user."""
    
    target_email = "iforgez@gmail.com"
    target_user_id = "user_2xaXl1ECHV80vYTdmiu6x3X66Wf"
    
    print(f"🔧 Complete fix for user: {target_email}")
    
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
        
        # 1. Fix subscription data (7-day trial as per AxWise standard)
        trial_start = datetime.now(timezone.utc)
        trial_end = trial_start + timedelta(days=7)
        user.usage_data["subscription"] = {
            "tier": "pro",
            "status": "trialing",
            "trial_end": trial_end.isoformat(),
            "start_date": trial_start.isoformat(),
            "admin_override": True  # Mark as admin fix
        }
        
        # 2. Ensure usage structure exists
        if "usage" not in user.usage_data:
            user.usage_data["usage"] = {}
        
        # 3. Add current month data with the analyses that were tracked
        # Based on logs: analyses 13, 14, 18 in June
        user.usage_data["usage"][current_month] = {
            "analyses_count": 3,  # User has run 3 analyses in June
            "prd_generations_count": 0,
            "analyses": [
                {
                    "analysis_id": 13,
                    "timestamp": "2025-06-03T19:32:44.269912"
                },
                {
                    "analysis_id": 14,
                    "timestamp": "2025-06-03T20:08:32.277485"
                },
                {
                    "analysis_id": 18,
                    "timestamp": "2025-06-04T10:40:41.908229"
                }
            ],
            "prd_generations": []
        }
        
        # 4. Set subscription status fields (already correct but ensure consistency)
        user.subscription_status = "trialing"
        if not user.subscription_id or user.subscription_id.startswith("admin_trial_"):
            user.subscription_id = f"admin_trial_{int(datetime.now(timezone.utc).timestamp())}"
        
        # 5. Mark the user object as dirty to ensure SQLAlchemy detects changes
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "usage_data")
        
        # 6. Force commit with explicit flush
        db.flush()
        db.commit()
        
        print(f"✅ Successfully fixed user data:")
        print(f"   - Subscription: Pro trial (100 analyses/month)")
        print(f"   - Current usage: 3/100 analyses used")
        print(f"   - Usage counter should show: '97/100 analyses'")
        print(f"   - Trial end: {trial_end.strftime('%Y-%m-%d %H:%M:%S UTC')} (7 days)")
        
        # Verify the fix by querying fresh from database
        db.refresh(user)
        print(f"\n🔍 Verification:")
        print(f"   - Database committed: ✅")
        if "subscription" in user.usage_data:
            print(f"   - Subscription tier: {user.usage_data['subscription']['tier']}")
            print(f"   - Trial end: {user.usage_data['subscription']['trial_end']}")
        if current_month in user.usage_data.get("usage", {}):
            current_usage = user.usage_data["usage"][current_month]["analyses_count"]
            print(f"   - Current month ({current_month}) analyses: {current_usage}")
        else:
            print(f"   - ⚠️ Current month data not found after commit")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error fixing user: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_iforgez_complete()
