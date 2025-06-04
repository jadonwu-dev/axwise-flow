#!/usr/bin/env python3
"""
Fix admin user trial period to standard 7 days
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

def fix_trial_period():
    """Fix admin user trial period to standard 7 days."""
    
    admin_user_id = "user_2xdZVfEfNCMGdl6ZsBLYYdCoWIw"
    admin_email = "vitalijs@axwise.de"
    
    print(f"🔧 Fixing trial period for admin user: {admin_email}")
    print(f"📅 Standard AxWise trial period: 7 days (not 30 days)")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Find the user
        user = db.query(User).filter(User.user_id == admin_user_id).first()
        
        if not user:
            print(f"❌ User {admin_user_id} not found!")
            return
        
        print(f"✅ Found user: {user.email}")
        
        # Check current trial end
        if user.usage_data and "subscription" in user.usage_data:
            current_trial_end = user.usage_data["subscription"].get("trial_end")
            print(f"📊 Current trial end: {current_trial_end}")
        else:
            print(f"❌ No subscription data found!")
            return
        
        # Set correct 7-day trial period
        trial_start = datetime.now(timezone.utc)
        trial_end = trial_start + timedelta(days=7)
        
        # Update subscription data with correct trial period
        user.usage_data["subscription"]["trial_end"] = trial_end.isoformat()
        user.usage_data["subscription"]["start_date"] = trial_start.isoformat()
        
        # Mark as dirty and commit
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "usage_data")
        
        db.flush()
        db.commit()
        
        print(f"✅ Successfully updated trial period:")
        print(f"   - Trial start: {trial_start.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"   - Trial end: {trial_end.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"   - Duration: 7 days (standard AxWise trial)")
        
        # Verify the fix
        db.refresh(user)
        updated_trial_end = user.usage_data["subscription"]["trial_end"]
        print(f"\n🔍 Verification:")
        print(f"   - Database committed: ✅")
        print(f"   - Updated trial end: {updated_trial_end}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error fixing trial period: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_trial_period()
