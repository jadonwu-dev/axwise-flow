#!/usr/bin/env python3
"""
Complete fix for admin user subscription and usage data
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

def fix_admin_complete():
    """Complete fix for admin user."""

    admin_user_id = "user_2xdZVfEfNCMGdl6ZsBLYYdCoWIw"
    admin_email = "vitalijs@axwise.de"

    print(f"🔧 Complete fix for admin user: {admin_email}")

    # Create database session
    db = SessionLocal()

    try:
        # Find the user
        user = db.query(User).filter(User.user_id == admin_user_id).first()

        if not user:
            print(f"❌ User {admin_user_id} not found!")
            return

        print(f"✅ Found user: {user.email}")

        # Get current month
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        print(f"📅 Current month: {current_month}")

        # Ensure usage_data exists
        if not user.usage_data:
            user.usage_data = {}

        # 1. Fix subscription data
        trial_end = datetime.now(timezone.utc) + timedelta(days=30)
        user.usage_data["subscription"] = {
            "tier": "pro",
            "status": "trialing",
            "trial_end": trial_end.isoformat(),
            "start_date": datetime.now(timezone.utc).isoformat(),
            "admin_override": True
        }

        # 2. Ensure usage structure exists
        if "usage" not in user.usage_data:
            user.usage_data["usage"] = {}

        # 3. Add current month data with the analyses that were tracked
        # Based on logs, you have analyses 15, 16, 17 in June
        user.usage_data["usage"][current_month] = {
            "analyses_count": 3,  # You've run 3 analyses in June
            "prd_generations_count": 0,
            "analyses": [
                {
                    "analysis_id": 15,
                    "timestamp": "2025-06-03T20:40:50.360796"
                },
                {
                    "analysis_id": 16,
                    "timestamp": "2025-06-04T09:33:06.449401"
                },
                {
                    "analysis_id": 17,
                    "timestamp": "2025-06-04T10:11:04.105874"
                }
            ],
            "prd_generations": []
        }

        # 4. Set subscription status fields
        user.subscription_status = "trialing"
        user.subscription_id = f"admin_trial_{int(datetime.now(timezone.utc).timestamp())}"

        # 5. Mark the user object as dirty to ensure SQLAlchemy detects changes
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "usage_data")

        # 6. Force commit with explicit flush
        db.flush()
        db.commit()

        print(f"✅ Successfully fixed admin user data:")
        print(f"   - Subscription: Pro trial (100 analyses/month)")
        print(f"   - Current usage: 3/100 analyses used")
        print(f"   - Usage counter should show: '97/100 analyses'")
        print(f"   - Trial end: {trial_end.strftime('%Y-%m-%d %H:%M:%S')}")

        # Verify the fix by querying fresh from database
        db.refresh(user)
        print(f"\n🔍 Verification:")
        print(f"   - Database committed: ✅")
        if "subscription" in user.usage_data:
            print(f"   - Subscription tier: {user.usage_data['subscription']['tier']}")
        if current_month in user.usage_data.get("usage", {}):
            current_usage = user.usage_data["usage"][current_month]["analyses_count"]
            print(f"   - Current month ({current_month}) analyses: {current_usage}")
        else:
            print(f"   - ⚠️ Current month data not found after commit")

    except Exception as e:
        db.rollback()
        print(f"❌ Error fixing admin user: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_complete()
