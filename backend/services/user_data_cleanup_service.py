"""
User Data Cleanup Service

This service automatically fixes common user data issues that can cause
checkout failures and other problems. It's designed to be called before
any critical operations like checkout, subscription management, etc.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from backend.models import User

logger = logging.getLogger(__name__)

class UserDataCleanupService:
    """Service to automatically fix user data issues."""
    
    def __init__(self, db: Session, user: User):
        """
        Initialize the cleanup service.
        
        Args:
            db: Database session
            user: User to clean up
        """
        self.db = db
        self.user = user
        
    def cleanup_user_data(self) -> Dict[str, Any]:
        """
        Perform comprehensive cleanup of user data.
        
        Returns:
            Dict with cleanup results and any issues found/fixed
        """
        results = {
            "user_id": self.user.user_id,
            "email": self.user.email,
            "issues_found": [],
            "fixes_applied": [],
            "status": "success"
        }
        
        try:
            # 1. Fix usage_data structure
            self._fix_usage_data_structure(results)
            
            # 2. Fix subscription data consistency
            self._fix_subscription_consistency(results)
            
            # 3. Clean up conflicting data
            self._clean_conflicting_data(results)
            
            # 4. Ensure proper defaults
            self._ensure_proper_defaults(results)
            
            # 5. Commit all changes
            if results["fixes_applied"]:
                # Mark usage_data as modified for SQLAlchemy
                flag_modified(self.user, "usage_data")
                self.db.commit()
                logger.info(f"Applied {len(results['fixes_applied'])} fixes for user {self.user.user_id}")
            
            return results
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during user data cleanup for {self.user.user_id}: {str(e)}")
            results["status"] = "error"
            results["error"] = str(e)
            return results
    
    def _fix_usage_data_structure(self, results: Dict[str, Any]) -> None:
        """Fix basic usage_data structure issues."""
        
        # Initialize usage_data if missing or invalid
        if not self.user.usage_data or not isinstance(self.user.usage_data, dict):
            results["issues_found"].append("Missing or invalid usage_data")
            self.user.usage_data = {}
            results["fixes_applied"].append("Initialized usage_data structure")
        
        # Ensure subscription section exists
        if "subscription" not in self.user.usage_data:
            results["issues_found"].append("Missing subscription section in usage_data")
            self.user.usage_data["subscription"] = {
                "tier": "free",
                "status": "active"
            }
            results["fixes_applied"].append("Added subscription section to usage_data")
        
        # Ensure usage section exists
        if "usage" not in self.user.usage_data:
            results["issues_found"].append("Missing usage section in usage_data")
            self.user.usage_data["usage"] = {}
            results["fixes_applied"].append("Added usage section to usage_data")
    
    def _fix_subscription_consistency(self, results: Dict[str, Any]) -> None:
        """Fix subscription data consistency issues."""
        
        subscription_info = self.user.usage_data.get("subscription", {})
        
        # Check for inconsistent subscription data
        has_subscription_status = bool(self.user.subscription_status)
        has_subscription_id = bool(self.user.subscription_id)
        has_usage_data_subscription = bool(subscription_info)
        
        # Case 1: User has subscription_status but no subscription_id
        if has_subscription_status and not has_subscription_id:
            results["issues_found"].append("Has subscription_status but no subscription_id")
            # Clear the orphaned subscription_status
            self.user.subscription_status = None
            results["fixes_applied"].append("Cleared orphaned subscription_status")
        
        # Case 2: User has subscription_id but no subscription_status
        if has_subscription_id and not has_subscription_status:
            results["issues_found"].append("Has subscription_id but no subscription_status")
            # This is more serious - log it but don't auto-fix
            logger.warning(f"User {self.user.user_id} has subscription_id {self.user.subscription_id} but no status")
        
        # Case 3: Subscription data exists but doesn't match usage_data
        if has_subscription_status and subscription_info:
            db_status = self.user.subscription_status
            usage_status = subscription_info.get("status")
            
            if db_status != usage_status:
                results["issues_found"].append(f"Subscription status mismatch: DB={db_status}, usage_data={usage_status}")
                # Trust the database status over usage_data
                self.user.usage_data["subscription"]["status"] = db_status
                results["fixes_applied"].append(f"Synced usage_data status to match DB: {db_status}")
    
    def _clean_conflicting_data(self, results: Dict[str, Any]) -> None:
        """Clean up conflicting or invalid data."""
        
        # Check for invalid subscription statuses
        valid_statuses = ["active", "trialing", "past_due", "canceled", "unpaid", "incomplete"]
        
        if self.user.subscription_status and self.user.subscription_status not in valid_statuses:
            results["issues_found"].append(f"Invalid subscription_status: {self.user.subscription_status}")
            self.user.subscription_status = None
            results["fixes_applied"].append("Cleared invalid subscription_status")
        
        # Check for invalid tier in usage_data
        subscription_info = self.user.usage_data.get("subscription", {})
        tier = subscription_info.get("tier")
        valid_tiers = ["free", "starter", "pro", "enterprise"]
        
        if tier and tier not in valid_tiers:
            results["issues_found"].append(f"Invalid tier in usage_data: {tier}")
            self.user.usage_data["subscription"]["tier"] = "free"
            results["fixes_applied"].append("Reset invalid tier to 'free'")
    
    def _ensure_proper_defaults(self, results: Dict[str, Any]) -> None:
        """Ensure proper default values are set."""
        
        subscription_info = self.user.usage_data.get("subscription", {})
        
        # Ensure tier is set
        if not subscription_info.get("tier"):
            self.user.usage_data["subscription"]["tier"] = "free"
            results["fixes_applied"].append("Set default tier to 'free'")
        
        # Ensure status is set
        if not subscription_info.get("status"):
            self.user.usage_data["subscription"]["status"] = "active"
            results["fixes_applied"].append("Set default status to 'active'")
        
        # Initialize current month usage if missing
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        usage_data = self.user.usage_data.get("usage", {})
        
        if current_month not in usage_data:
            self.user.usage_data["usage"][current_month] = {
                "analyses_count": 0,
                "prd_generations_count": 0,
                "analyses": [],
                "prd_generations": []
            }
            results["fixes_applied"].append(f"Initialized usage tracking for {current_month}")
    
    def is_ready_for_checkout(self) -> tuple[bool, list[str]]:
        """
        Check if user is ready for checkout operations.
        
        Returns:
            Tuple of (is_ready, list_of_issues)
        """
        issues = []
        
        # Check basic user data
        if not self.user.email:
            issues.append("User email is missing")
        
        # Check usage_data structure
        if not self.user.usage_data or not isinstance(self.user.usage_data, dict):
            issues.append("Invalid usage_data structure")
        
        # Check subscription section
        subscription_info = self.user.usage_data.get("subscription", {}) if self.user.usage_data else {}
        if not subscription_info:
            issues.append("Missing subscription section in usage_data")
        
        # Check for conflicting subscription data
        if self.user.subscription_status and not self.user.subscription_id:
            issues.append("Has subscription_status but no subscription_id")
        
        return len(issues) == 0, issues
    
    @classmethod
    def cleanup_and_prepare_for_checkout(cls, db: Session, user: User) -> Dict[str, Any]:
        """
        Convenience method to cleanup user data and prepare for checkout.
        
        Args:
            db: Database session
            user: User to prepare
            
        Returns:
            Dict with cleanup results
        """
        service = cls(db, user)
        
        # First, cleanup any issues
        cleanup_results = service.cleanup_user_data()
        
        # Then check if ready for checkout
        is_ready, checkout_issues = service.is_ready_for_checkout()
        
        cleanup_results["checkout_ready"] = is_ready
        cleanup_results["checkout_issues"] = checkout_issues
        
        return cleanup_results
