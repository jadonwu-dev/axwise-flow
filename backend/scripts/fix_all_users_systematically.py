#!/usr/bin/env python3
"""
Systematic fix for ALL users in the database

This script identifies and fixes common user data issues that can cause
checkout failures, usage tracking problems, and other systematic issues.
"""

import sys
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.models import User
from backend.services.user_data_cleanup_service import UserDataCleanupService

# Production database URL
PRODUCTION_DATABASE_URL=***REDACTED***

# Create production database session
engine = create_engine(PRODUCTION_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_all_users():
    """Fix all users in the database systematically."""
    
    print(f"🔧 Starting systematic fix for ALL users in database")
    print(f"📅 Timestamp: {datetime.now(timezone.utc).isoformat()}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get all users
        all_users = db.query(User).all()
        total_users = len(all_users)
        
        print(f"📊 Found {total_users} users to process")
        
        if total_users == 0:
            print("❌ No users found in database!")
            return
        
        # Track statistics
        stats = {
            "total_users": total_users,
            "users_with_issues": 0,
            "users_fixed": 0,
            "total_fixes_applied": 0,
            "errors": 0,
            "checkout_ready_before": 0,
            "checkout_ready_after": 0
        }
        
        print(f"\n🔍 Processing users...")
        
        for i, user in enumerate(all_users, 1):
            print(f"\n[{i}/{total_users}] Processing user: {user.email} ({user.user_id})")
            
            try:
                # Check if user was ready for checkout before cleanup
                service = UserDataCleanupService(db, user)
                was_ready_before, issues_before = service.is_ready_for_checkout()
                if was_ready_before:
                    stats["checkout_ready_before"] += 1
                
                # Perform cleanup
                cleanup_results = service.cleanup_user_data()
                
                # Track results
                issues_found = cleanup_results.get("issues_found", [])
                fixes_applied = cleanup_results.get("fixes_applied", [])
                
                if issues_found:
                    stats["users_with_issues"] += 1
                    print(f"   🐛 Issues found: {len(issues_found)}")
                    for issue in issues_found:
                        print(f"      - {issue}")
                
                if fixes_applied:
                    stats["users_fixed"] += 1
                    stats["total_fixes_applied"] += len(fixes_applied)
                    print(f"   ✅ Fixes applied: {len(fixes_applied)}")
                    for fix in fixes_applied:
                        print(f"      - {fix}")
                else:
                    print(f"   ✅ No issues found - user data is clean")
                
                # Check if user is ready for checkout after cleanup
                is_ready_after, issues_after = service.is_ready_for_checkout()
                if is_ready_after:
                    stats["checkout_ready_after"] += 1
                
                if not is_ready_after:
                    print(f"   ⚠️ Still has checkout issues after cleanup:")
                    for issue in issues_after:
                        print(f"      - {issue}")
                
                # Show current user status
                subscription_info = user.usage_data.get("subscription", {}) if user.usage_data else {}
                tier = subscription_info.get("tier", "unknown")
                status = subscription_info.get("status", "unknown")
                print(f"   📊 Final status: tier={tier}, status={status}, checkout_ready={is_ready_after}")
                
            except Exception as e:
                stats["errors"] += 1
                print(f"   ❌ Error processing user: {str(e)}")
                continue
        
        # Print final statistics
        print(f"\n" + "="*60)
        print(f"📊 SYSTEMATIC FIX COMPLETE")
        print(f"="*60)
        print(f"Total users processed: {stats['total_users']}")
        print(f"Users with issues found: {stats['users_with_issues']}")
        print(f"Users successfully fixed: {stats['users_fixed']}")
        print(f"Total fixes applied: {stats['total_fixes_applied']}")
        print(f"Errors encountered: {stats['errors']}")
        print(f"")
        print(f"Checkout readiness:")
        print(f"  Before cleanup: {stats['checkout_ready_before']}/{stats['total_users']} ({stats['checkout_ready_before']/stats['total_users']*100:.1f}%)")
        print(f"  After cleanup:  {stats['checkout_ready_after']}/{stats['total_users']} ({stats['checkout_ready_after']/stats['total_users']*100:.1f}%)")
        print(f"  Improvement: +{stats['checkout_ready_after'] - stats['checkout_ready_before']} users")
        
        if stats["errors"] == 0:
            print(f"\n✅ All users processed successfully!")
        else:
            print(f"\n⚠️ {stats['errors']} errors encountered during processing")
        
        print(f"\n🎯 Impact:")
        print(f"  - Checkout failures should be significantly reduced")
        print(f"  - Usage tracking will work properly for all users")
        print(f"  - Subscription management will be more reliable")
        print(f"  - New users will have clean data from the start")
        
    except Exception as e:
        print(f"❌ Critical error during mass user fix: {str(e)}")
        raise
    finally:
        db.close()

def show_user_issues_summary():
    """Show a summary of common user issues without fixing them."""
    
    print(f"🔍 Analyzing user data issues (read-only)")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get all users
        all_users = db.query(User).all()
        total_users = len(all_users)
        
        print(f"📊 Analyzing {total_users} users...")
        
        # Track issue types
        issue_types = {}
        users_with_issues = 0
        checkout_ready_count = 0
        
        for user in all_users:
            service = UserDataCleanupService(db, user)
            is_ready, issues = service.is_ready_for_checkout()
            
            if is_ready:
                checkout_ready_count += 1
            
            # Simulate cleanup to see what issues would be found
            cleanup_results = {
                "issues_found": [],
                "fixes_applied": []
            }
            
            # Check for issues without fixing them
            if not user.usage_data or not isinstance(user.usage_data, dict):
                cleanup_results["issues_found"].append("Missing or invalid usage_data")
            
            if user.usage_data and "subscription" not in user.usage_data:
                cleanup_results["issues_found"].append("Missing subscription section")
            
            if user.subscription_status and not user.subscription_id:
                cleanup_results["issues_found"].append("Has subscription_status but no subscription_id")
            
            # Count issue types
            if cleanup_results["issues_found"]:
                users_with_issues += 1
                for issue in cleanup_results["issues_found"]:
                    issue_types[issue] = issue_types.get(issue, 0) + 1
        
        # Print summary
        print(f"\n📊 ISSUE ANALYSIS SUMMARY")
        print(f"="*50)
        print(f"Total users: {total_users}")
        print(f"Users with issues: {users_with_issues}")
        print(f"Users ready for checkout: {checkout_ready_count}")
        print(f"Users needing fixes: {total_users - checkout_ready_count}")
        
        if issue_types:
            print(f"\n🐛 Common issues found:")
            for issue, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {count:3d} users: {issue}")
        else:
            print(f"\n✅ No common issues found!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--analyze-only":
        show_user_issues_summary()
    else:
        fix_all_users()
