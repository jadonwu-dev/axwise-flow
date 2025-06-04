#!/usr/bin/env python3
"""
Quick fix for admin user subscription data

This script specifically fixes the admin user (vitalijs@axwise.de) to have Pro trial limits.
"""

import sys
import os
from datetime import datetime, timedelta
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

def fix_admin_user():
    """Fix the admin user's subscription data."""

    # Target user (correct user ID from production database)
    admin_user_id = "user_2xdZVfEfNCMGdl6ZsBLYYdCoWIw"
    admin_email = "vitalijs@axwise.de"

    print(f"🔧 Fixing subscription data for admin user: {admin_email}")

    # Create database session
    db = SessionLocal()

    try:
        # Find the user
        user = db.query(User).filter(User.user_id == admin_user_id).first()

        if not user:
            print(f"❌ User {admin_user_id} not found!")
            return

        print(f"✅ Found user: {user.email}")
        print(f"📊 Current subscription_status: {user.subscription_status}")
        print(f"📊 Current subscription_id: {user.subscription_id}")
        print(f"📊 Current usage_data: {user.usage_data}")

        # Create Pro trial subscription data
        trial_end = datetime.now() + timedelta(days=30)  # 30 days trial

        # Ensure usage_data exists
        if not user.usage_data:
            user.usage_data = {}

        # Set Pro trial subscription data
        user.usage_data["subscription"] = {
            "tier": "pro",
            "status": "trialing",
            "trial_end": trial_end.isoformat(),
            "start_date": datetime.now().isoformat(),
            "admin_override": True  # Mark this as admin override
        }

        # Also set the subscription status fields
        user.subscription_status = "trialing"
        user.subscription_id = f"admin_trial_{int(datetime.now().timestamp())}"

        # Commit changes
        db.commit()

        print(f"✅ Successfully updated admin user subscription data:")
        print(f"   - Tier: pro")
        print(f"   - Status: trialing")
        print(f"   - Trial end: {trial_end.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - Analyses limit: 100 per month")
        print(f"   - PRD limit: Unlimited")

        print(f"\n🎉 Admin user now has Pro trial limits!")
        print(f"   Usage counter should show: 'X/100 analyses'")

    except Exception as e:
        db.rollback()
        print(f"❌ Error fixing admin user: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_user()
