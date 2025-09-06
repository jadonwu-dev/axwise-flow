import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def now_ms() -> int:
    return int(time.time() * 1000)


def request_start(endpoint: str, user_id: Optional[str] = None, session_id: Optional[str] = None, **additional_fields: Any) -> float:
    """
    Emit a structured request_start log and return the start_time (epoch seconds) for duration calculation.
    """
    start_time = time.time()
    payload: Dict[str, Any] = {
        "event": "request_start",
        "endpoint": endpoint,
        "user_id": user_id,
        "session_id": session_id,
    }
    if additional_fields:
        payload.update(additional_fields)
    logger.info(json.dumps(payload))
    return start_time


def request_end(endpoint: str, start_time: float, user_id: Optional[str] = None, session_id: Optional[str] = None, http_status: int = 200, **additional_fields: Any) -> None:
    """
    Emit a structured request_end log with response_time_ms.
    """
    response_time_ms = int((time.time() - start_time) * 1000)
    payload: Dict[str, Any] = {
        "event": "request_end",
        "endpoint": endpoint,
        "user_id": user_id,
        "session_id": session_id,
        "http_status": http_status,
        "response_time_ms": response_time_ms,
    }
    if additional_fields:
        payload.update(additional_fields)
    logger.info(json.dumps(payload))


def request_error(endpoint: str, start_time: float, user_id: Optional[str] = None, session_id: Optional[str] = None, http_status: int = 500, error: Optional[str] = None, **additional_fields: Any) -> None:
    """
    Emit a structured request_error log with response_time_ms and error message.
    """
    response_time_ms = int((time.time() - start_time) * 1000)
    payload: Dict[str, Any] = {
        "event": "request_error",
        "endpoint": endpoint,
        "user_id": user_id,
        "session_id": session_id,
        "http_status": http_status,
        "response_time_ms": response_time_ms,
    }
    if error is not None:
        payload["error"] = error
    if additional_fields:
        payload.update(additional_fields)
    # Use warning for 4xx, error for 5xx
    if 400 <= http_status < 500:
        logger.warning(json.dumps(payload))
    else:
        logger.error(json.dumps(payload))

