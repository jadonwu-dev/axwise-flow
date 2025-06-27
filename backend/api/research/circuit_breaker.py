"""
Circuit Breaker Pattern for Research Enhancements
Provides reliability and automatic fallback for V3 enhancements.
"""

import logging
import time
from typing import Dict, Set, Any, Callable, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class EnhancementStats:
    """Statistics for an enhancement"""
    success_count: int = 0
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate (0.0 to 1.0)"""
        total = self.success_count + self.failure_count
        return self.failure_count / total if total > 0 else 0.0
    
    @property
    def total_calls(self) -> int:
        """Total number of calls"""
        return self.success_count + self.failure_count


class CircuitBreaker:
    """
    Circuit breaker for research enhancements.
    
    States:
    - CLOSED: Normal operation, enhancement enabled
    - OPEN: Enhancement disabled due to failures
    - HALF_OPEN: Testing if enhancement has recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 3,
        failure_rate_threshold: float = 0.5,
        recovery_timeout: int = 60,
        min_calls_for_rate_check: int = 5
    ):
        self.failure_threshold = failure_threshold
        self.failure_rate_threshold = failure_rate_threshold
        self.recovery_timeout = recovery_timeout
        self.min_calls_for_rate_check = min_calls_for_rate_check
        
        self.stats: Dict[str, EnhancementStats] = {}
        self.disabled_enhancements: Set[str] = set()
        
        logger.info(f"🔧 Circuit breaker initialized - failure_threshold: {failure_threshold}, "
                   f"failure_rate_threshold: {failure_rate_threshold}")
    
    def is_enabled(self, enhancement_name: str) -> bool:
        """Check if enhancement is enabled (circuit closed)"""
        if enhancement_name in self.disabled_enhancements:
            # Check if recovery timeout has passed
            stats = self.stats.get(enhancement_name)
            if stats and stats.last_failure_time:
                time_since_failure = time.time() - stats.last_failure_time
                if time_since_failure > self.recovery_timeout:
                    logger.info(f"🔄 Attempting recovery for {enhancement_name} after {time_since_failure:.1f}s")
                    self.disabled_enhancements.remove(enhancement_name)
                    return True
            return False
        return True
    
    def record_success(self, enhancement_name: str):
        """Record successful enhancement execution"""
        if enhancement_name not in self.stats:
            self.stats[enhancement_name] = EnhancementStats()
        
        self.stats[enhancement_name].success_count += 1
        self.stats[enhancement_name].last_success_time = time.time()
        
        # If it was disabled and now successful, keep it enabled
        if enhancement_name in self.disabled_enhancements:
            logger.info(f"✅ {enhancement_name} recovered successfully")
    
    def record_failure(self, enhancement_name: str, error: Exception):
        """Record failed enhancement execution"""
        if enhancement_name not in self.stats:
            self.stats[enhancement_name] = EnhancementStats()
        
        stats = self.stats[enhancement_name]
        stats.failure_count += 1
        stats.last_failure_time = time.time()
        
        logger.warning(f"❌ {enhancement_name} failed: {error}")
        
        # Check if we should disable the enhancement
        should_disable = False
        
        # Rule 1: Too many consecutive failures
        if stats.failure_count >= self.failure_threshold:
            should_disable = True
            reason = f"failure count ({stats.failure_count}) >= threshold ({self.failure_threshold})"
        
        # Rule 2: High failure rate with sufficient data
        elif (stats.total_calls >= self.min_calls_for_rate_check and 
              stats.failure_rate >= self.failure_rate_threshold):
            should_disable = True
            reason = f"failure rate ({stats.failure_rate:.2f}) >= threshold ({self.failure_rate_threshold})"
        
        if should_disable and enhancement_name not in self.disabled_enhancements:
            self.disabled_enhancements.add(enhancement_name)
            logger.error(f"🚫 Disabling {enhancement_name}: {reason}")
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all enhancements"""
        return {
            name: {
                "success_count": stats.success_count,
                "failure_count": stats.failure_count,
                "failure_rate": stats.failure_rate,
                "total_calls": stats.total_calls,
                "is_enabled": name not in self.disabled_enhancements,
                "last_failure_time": stats.last_failure_time,
                "last_success_time": stats.last_success_time
            }
            for name, stats in self.stats.items()
        }
    
    async def execute_with_fallback(
        self,
        enhancement_name: str,
        enhancement_func: Callable,
        fallback_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute enhancement with automatic fallback.
        
        Args:
            enhancement_name: Name of the enhancement for tracking
            enhancement_func: Function to try (V3 enhancement)
            fallback_func: Function to fall back to (V1 core)
            *args, **kwargs: Arguments for both functions
        """
        if not self.is_enabled(enhancement_name):
            logger.info(f"⚡ {enhancement_name} disabled, using fallback")
            return await fallback_func(*args, **kwargs)
        
        try:
            result = await enhancement_func(*args, **kwargs)
            self.record_success(enhancement_name)
            return result
        except Exception as e:
            self.record_failure(enhancement_name, e)
            logger.warning(f"🔄 {enhancement_name} failed, falling back to V1: {e}")
            return await fallback_func(*args, **kwargs)


# Global circuit breaker instance
circuit_breaker = CircuitBreaker()
