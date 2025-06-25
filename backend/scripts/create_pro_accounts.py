#!/usr/bin/env python3
"""
Create Pro accounts for Typhanie and Andrew without trial periods

This script creates full Pro accounts for specific users, bypassing the trial system.
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
    "postgresql://USER:PASS@HOST:PORT/DB
)

# Create production database session
engine = create_engine(PRODUCTION_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_pro_account(user_id: str, email: str, name: str):
    """Create a Pro account for a specific user."""

    print(f"🚀 Creating Pro account for: {name} ({email})")

    # Create database session
    db = SessionLocal()

    try:
        # Find the user
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            print(f"❌ User {user_id} not found!")
            return False

        print(f"✅ Found user: {user.email}")
        print(f"📊 Current subscription_status: {user.subscription_status}")
        print(f"📊 Current subscription_id: {user.subscription_id}")
        print(f"📊 Current usage_data: {user.usage_data}")

        # Get current month
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")

        # Ensure usage_data exists
        if not user.usage_data:
            user.usage_data = {}

        # Create Pro subscription data (active, not trial)
        start_date = datetime.now(timezone.utc)

        # Set Pro subscription data
        user.usage_data["subscription"] = {
            "tier": "pro",
            "status": "active",  # Active, not trialing
            "start_date": start_date.isoformat(),
            "admin_override": True,  # Mark this as admin override
            "created_by": "admin_script",
            "notes": f"Pro account created for {name} without trial",
        }

        # Initialize usage structure for current month
        if "usage" not in user.usage_data:
            user.usage_data["usage"] = {}

        if current_month not in user.usage_data["usage"]:
            user.usage_data["usage"][current_month] = {"analyses": 0, "prds": 0}

        # Set subscription status fields
        user.subscription_status = "active"
        user.subscription_id = f"admin_pro_{int(start_date.timestamp())}"

        # Mark the user object as dirty to ensure SQLAlchemy detects changes
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(user, "usage_data")

        # Force commit with explicit flush
        db.flush()
        db.commit()

        print(f"✅ Successfully created Pro account for {name}:")
        print(f"   - Tier: Pro")
        print(f"   - Status: Active (no trial)")
        print(f"   - Start date: {start_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"   - Analyses limit: 100 per month")
        print(f"   - PRD limit: Unlimited")
        print(f"   - Current usage: 0/100 analyses, 0 PRDs")

        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating Pro account for {name}: {str(e)}")
        return False
    finally:
        db.close()


def main():
    """Create Pro accounts for Typhanie and Andrew."""

    # User details with actual Clerk user IDs from production database
    users_to_create = [
        {
            "user_id": "user_2yikc3smEzcTqn2sx5YANNF1KMZ",  # Typhanie's actual Clerk user ID
            "email": "typhanie.cochrane@gmail.com",  # Typhanie's actual email
            "name": "Typhanie",
        },
        {
            "user_id": "user_2y8USSgyApT3B4QN3ACtbuT1fqr",  # Andrew's actual Clerk user ID
            "email": "tominav@gmail.com",  # Andrew's actual email (Andrew Tomin)
            "name": "Andrew",
        },
    ]

    print("🎯 Creating Pro accounts for Typhanie and Andrew")
    print("=" * 50)

    success_count = 0

    for user_info in users_to_create:
        if user_info["user_id"].startswith("REPLACE_"):
            print(
                f"⚠️  Skipping {user_info['name']} - user_id needs to be updated with actual Clerk ID"
            )
            continue

        success = create_pro_account(
            user_info["user_id"], user_info["email"], user_info["name"]
        )

        if success:
            success_count += 1

        print("-" * 30)

    print(f"\n🎉 Successfully created {success_count} Pro accounts!")
    print("Users now have full Pro access without trial limitations.")


if __name__ == "__main__":
    main()
