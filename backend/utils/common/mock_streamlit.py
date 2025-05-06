"""
Mock streamlit module for backend services.

This module provides mock implementations of streamlit functions
to allow backend services to run without streamlit dependencies.
"""

import logging
from typing import Any, Dict, Optional, List, Callable

logger = logging.getLogger(__name__)

class SessionState:
    """Mock session state for streamlit"""
    _state: Dict[str, Any] = {}
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a value from session state"""
        return cls._state.get(key, default)
    
    @classmethod
    def __getitem__(cls, key: str) -> Any:
        """Get a value from session state using [] syntax"""
        return cls._state.get(key)
    
    @classmethod
    def __setitem__(cls, key: str, value: Any) -> None:
        """Set a value in session state using [] syntax"""
        cls._state[key] = value

# Create mock session_state
session_state = SessionState()

# Mock streamlit functions
def text(*args: Any, **kwargs: Any) -> None:
    """Mock st.text()"""
    logger.debug(f"Mock st.text called with: {args}")

def progress(*args: Any, **kwargs: Any) -> None:
    """Mock st.progress()"""
    logger.debug(f"Mock st.progress called with: {args}")

def success(*args: Any, **kwargs: Any) -> None:
    """Mock st.success()"""
    logger.debug(f"Mock st.success called with: {args}")

def error(*args: Any, **kwargs: Any) -> None:
    """Mock st.error()"""
    logger.debug(f"Mock st.error called with: {args}")

def warning(*args: Any, **kwargs: Any) -> None:
    """Mock st.warning()"""
    logger.debug(f"Mock st.warning called with: {args}")

def info(*args: Any, **kwargs: Any) -> None:
    """Mock st.info()"""
    logger.debug(f"Mock st.info called with: {args}")

class MockExpander:
    """Mock expander for streamlit"""
    def __init__(self, *args: Any, **kwargs: Any):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass
    
    def code(self, *args: Any, **kwargs: Any) -> None:
        """Mock expander.code()"""
        pass

def expander(*args: Any, **kwargs: Any) -> MockExpander:
    """Mock st.expander()"""
    return MockExpander()

def metric(*args: Any, **kwargs: Any) -> None:
    """Mock st.metric()"""
    logger.debug(f"Mock st.metric called with: {args}")

def plotly_chart(*args: Any, **kwargs: Any) -> None:
    """Mock st.plotly_chart()"""
    logger.debug(f"Mock st.plotly_chart called with: {args}")

def markdown(*args: Any, **kwargs: Any) -> None:
    """Mock st.markdown()"""
    logger.debug(f"Mock st.markdown called with: {args}")

def columns(*args: Any, **kwargs: Any) -> List[Any]:
    """Mock st.columns()"""
    class MockColumn:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    
    # Return a list of mock columns
    return [MockColumn() for _ in range(args[0] if args else 1)]

def subheader(*args: Any, **kwargs: Any) -> None:
    """Mock st.subheader()"""
    logger.debug(f"Mock st.subheader called with: {args}")

class MockSecrets:
    """Mock REDACTED_SECRETs for streamlit"""
    _REDACTED_SECRETs: Dict[str, Any] = {}
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a REDACTED_SECRET value"""
        return cls._REDACTED_SECRETs.get(key, default)
    
    @classmethod
    def __getitem__(cls, key: str) -> Any:
        """Get a REDACTED_SECRET value using [] syntax"""
        return cls._REDACTED_SECRETs.get(key)

# Create mock REDACTED_SECRETs
REDACTED_SECRETs = MockSecrets()
