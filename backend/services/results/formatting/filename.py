from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session


def get_filename_for_data_id(db: Session, data_id: Any) -> str:
    """Fetch InterviewData filename by id; returns "Unknown" if not found."""
    if not data_id:
        return "Unknown"
    try:
        from backend.models import InterviewData

        row = db.query(InterviewData).filter(InterviewData.id == data_id).first()
        if row:
            return row.filename or "Unknown"
        return "Unknown"
    except Exception:
        return "Unknown"

