#!/usr/bin/env python3
"""
Database Migration Script: Fix Trial Users Subscription Data

This script identifies users who have trial-related subscription data but missing
or incorrect usage_data, and fixes their subscription information.

Usage:
    python -m backend.scripts.fix_trial_users [--dry-run] [--verbose]

Options:
    --dry-run    Show what would be changed without making actual changes
    --verbose    Show detailed logging information
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.database import SessionLocal, engine
from backend.models import User
from sqlalchemy import text
from sqlalchemy.orm import Session

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_trial_users(db: Session) -> List[User]:
    """
    Find users who have trial-related subscription data.
    
    Returns:
        List of User objects that have trial indicators
    """
    logger.info("🔍 Searching for users with trial-related data...")
    
    # Find users with subscription_status indicating trial or subscription_id
    trial_users = db.query(User).filter(
        (User.subscription_status.isnot(None)) |
        (User.subscription_id.isnot(None))
    ).all()
    
    logger.info(f"Found {len(trial_users)} users with subscription data")
    
    # Log details for each user
    for user in trial_users:
        logger.info(f"  - {user.user_id} ({user.email}): status={user.subscription_status}, id={user.subscription_id}")
    
    return trial_users


def analyze_user_subscription_data(user: User) -> Dict[str, Any]:
    """
    Analyze a user's current subscription data and determine what needs to be fixed.
    
    Args:
        user: User object to analyze
        
    Returns:
        Dictionary with analysis results and recommended actions
    """
    analysis = {
        "user_id": user.user_id,
        "email": user.email,
        "current_subscription_status": user.subscription_status,
        "current_subscription_id": user.subscription_id,
        "current_usage_data": user.usage_data,
        "needs_fix": False,
        "recommended_action": "none",
        "new_usage_data": None
    }
    
    # Check if user has subscription indicators but missing/incorrect usage_data
    has_subscription_status = user.subscription_status is not None
    has_subscription_id = user.subscription_id is not None
    has_usage_data_subscription = (
        user.usage_data and 
        isinstance(user.usage_data, dict) and 
        "subscription" in user.usage_data and
        isinstance(user.usage_data["subscription"], dict)
    )
    
    # Determine if this is a trial user
    is_trial_user = (
        user.subscription_status == "trialing" or
        (has_subscription_id and user.subscription_status in ["active", "trialing"])
    )
    
    if is_trial_user:
        # This is a trial user - check if usage_data is correct
        if not has_usage_data_subscription:
            analysis["needs_fix"] = True
            analysis["recommended_action"] = "create_trial_usage_data"
        else:
            # Check if usage_data subscription info is correct
            subscription_data = user.usage_data["subscription"]
            current_tier = subscription_data.get("tier", "free")
            current_status = subscription_data.get("status", "inactive")
            
            if current_tier == "free" or current_status != user.subscription_status:
                analysis["needs_fix"] = True
                analysis["recommended_action"] = "update_trial_usage_data"
    
    elif has_subscription_status or has_subscription_id:
        # User has some subscription data but not trialing - might be expired trial
        if user.subscription_status in ["canceled", "incomplete", "incomplete_expired", "past_due", "unpaid"]:
            analysis["recommended_action"] = "reset_to_free"
            analysis["needs_fix"] = True
        elif user.subscription_status == "active":
            # Active subscription - ensure usage_data reflects this
            if not has_usage_data_subscription:
                analysis["needs_fix"] = True
                analysis["recommended_action"] = "create_active_usage_data"
    
    # Generate new usage_data if needed
    if analysis["needs_fix"]:
        analysis["new_usage_data"] = generate_usage_data(user, analysis["recommended_action"])
    
    return analysis


def generate_usage_data(user: User, action: str) -> Dict[str, Any]:
    """
    Generate the correct usage_data structure based on the recommended action.
    
    Args:
        user: User object
        action: Recommended action from analysis
        
    Returns:
        New usage_data dictionary
    """
    # Preserve existing usage data if it exists
    base_usage_data = user.usage_data if user.usage_data else {}
    if not isinstance(base_usage_data, dict):
        base_usage_data = {}
    
    # Ensure usage section exists
    if "usage" not in base_usage_data:
        base_usage_data["usage"] = {}
    
    # Generate subscription data based on action
    if action == "create_trial_usage_data":
        # Create trial subscription data
        trial_end = datetime.now() + timedelta(days=7)
        base_usage_data["subscription"] = {
            "tier": "pro",
            "status": user.subscription_status or "trialing",
            "trial_end": trial_end.isoformat(),
            "start_date": datetime.now().isoformat()
        }
        
    elif action == "update_trial_usage_data":
        # Update existing subscription data for trial
        if "subscription" not in base_usage_data:
            base_usage_data["subscription"] = {}
        
        base_usage_data["subscription"].update({
            "tier": "pro",
            "status": user.subscription_status or "trialing"
        })
        
        # Add trial_end if missing
        if "trial_end" not in base_usage_data["subscription"]:
            trial_end = datetime.now() + timedelta(days=7)
            base_usage_data["subscription"]["trial_end"] = trial_end.isoformat()
    
    elif action == "create_active_usage_data":
        # Create active subscription data
        base_usage_data["subscription"] = {
            "tier": "pro",  # Assume Pro for active subscriptions
            "status": user.subscription_status,
            "start_date": datetime.now().isoformat()
        }
    
    elif action == "reset_to_free":
        # Reset to free tier
        base_usage_data["subscription"] = {
            "tier": "free",
            "status": "active"
        }
    
    return base_usage_data


def apply_fixes(db: Session, analyses: List[Dict[str, Any]], dry_run: bool = True) -> None:
    """
    Apply the recommended fixes to users.
    
    Args:
        db: Database session
        analyses: List of user analyses with recommended fixes
        dry_run: If True, only show what would be changed without making changes
    """
    users_to_fix = [analysis for analysis in analyses if analysis["needs_fix"]]
    
    if not users_to_fix:
        logger.info("✅ No users need fixing!")
        return
    
    logger.info(f"{'🔍 DRY RUN: Would fix' if dry_run else '🔧 Fixing'} {len(users_to_fix)} users:")
    
    for analysis in users_to_fix:
        user_id = analysis["user_id"]
        email = analysis["email"]
        action = analysis["recommended_action"]
        new_usage_data = analysis["new_usage_data"]
        
        logger.info(f"  - {user_id} ({email}): {action}")
        
        if not dry_run:
            # Apply the fix
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                user.usage_data = new_usage_data
                logger.info(f"    ✅ Updated usage_data for {user_id}")
            else:
                logger.error(f"    ❌ User {user_id} not found!")
    
    if not dry_run:
        try:
            db.commit()
            logger.info(f"✅ Successfully applied fixes to {len(users_to_fix)} users")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error applying fixes: {str(e)}")
            raise


def main():
    """Main function to run the migration script."""
    parser = argparse.ArgumentParser(description="Fix trial users subscription data")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🚀 Starting trial users subscription data fix...")
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE CHANGES'}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Step 1: Find trial users
        trial_users = get_trial_users(db)
        
        if not trial_users:
            logger.info("✅ No users with subscription data found. Nothing to fix.")
            return
        
        # Step 2: Analyze each user
        logger.info("📊 Analyzing user subscription data...")
        analyses = []
        
        for user in trial_users:
            analysis = analyze_user_subscription_data(user)
            analyses.append(analysis)
            
            if args.verbose:
                logger.debug(f"Analysis for {user.user_id}: {analysis}")
        
        # Step 3: Apply fixes
        apply_fixes(db, analyses, dry_run=args.dry_run)
        
        # Step 4: Summary
        total_users = len(analyses)
        users_needing_fix = len([a for a in analyses if a["needs_fix"]])
        
        logger.info("📈 Summary:")
        logger.info(f"  - Total users with subscription data: {total_users}")
        logger.info(f"  - Users needing fixes: {users_needing_fix}")
        logger.info(f"  - Users already correct: {total_users - users_needing_fix}")
        
        if args.dry_run and users_needing_fix > 0:
            logger.info("🔄 To apply these changes, run the script without --dry-run")
        
    except Exception as e:
        logger.error(f"❌ Error during migration: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
