"""
Announcement endpoints for public display and teacher-managed CRUD operations.
"""

from datetime import date
import html
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


def _validate_teacher_session(teacher_username: Optional[str]) -> Dict[str, Any]:
    if not teacher_username:
        raise HTTPException(status_code=401, detail="Authentication required")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    return teacher


def _parse_iso_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} must use YYYY-MM-DD format"
        ) from error


def _validate_announcement_payload(payload: Dict[str, Any]) -> Dict[str, str]:
    title = html.escape(str(payload.get("title", "")).strip())
    message = html.escape(str(payload.get("message", "")).strip())
    expiration_date = str(payload.get("expiration_date", "")).strip()
    start_date_raw = str(payload.get("start_date", "")).strip()

    if not title:
        raise HTTPException(status_code=422, detail="Title is required")
    if not message:
        raise HTTPException(status_code=422, detail="Message is required")
    if len(title) > 120:
        raise HTTPException(status_code=422, detail="Title is too long")
    if len(message) > 500:
        raise HTTPException(status_code=422, detail="Message is too long")
    if not expiration_date:
        raise HTTPException(status_code=422, detail="Expiration date is required")

    parsed_expiration = _parse_iso_date(expiration_date, "expiration_date")

    start_date = ""
    if start_date_raw:
        parsed_start = _parse_iso_date(start_date_raw, "start_date")
        if parsed_start > parsed_expiration:
            raise HTTPException(
                status_code=422,
                detail="start_date must be on or before expiration_date"
            )
        start_date = parsed_start.isoformat()

    return {
        "title": title,
        "message": message,
        "start_date": start_date,
        "expiration_date": parsed_expiration.isoformat()
    }


def _announcement_to_response(document: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(document.get("_id", "")),
        "title": document.get("title", ""),
        "message": document.get("message", ""),
        "start_date": document.get("start_date", ""),
        "expiration_date": document.get("expiration_date", "")
    }


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Return only currently active announcements for public display."""
    today = date.today().isoformat()

    query = {
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": ""},
            {"start_date": {"$exists": False}},
            {"start_date": {"$lte": today}}
        ]
    }

    documents = announcements_collection.find(query).sort("expiration_date", 1)
    return [_announcement_to_response(doc) for doc in documents]


@router.get("/manage", response_model=List[Dict[str, Any]])
def get_all_announcements(teacher_username: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all announcements for authenticated teachers/admins."""
    _validate_teacher_session(teacher_username)
    documents = announcements_collection.find().sort("expiration_date", 1)
    return [_announcement_to_response(doc) for doc in documents]


@router.post("")
@router.post("/")
def create_announcement(payload: Dict[str, Any], teacher_username: Optional[str] = None) -> Dict[str, str]:
    """Create a new announcement (requires authentication)."""
    _validate_teacher_session(teacher_username)
    clean_payload = _validate_announcement_payload(payload)

    announcement_id = f"ann-{uuid4().hex[:12]}"
    announcements_collection.insert_one({"_id": announcement_id, **clean_payload})
    return {"message": "Announcement created", "id": announcement_id}


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    payload: Dict[str, Any],
    teacher_username: Optional[str] = None
) -> Dict[str, str]:
    """Update an existing announcement (requires authentication)."""
    _validate_teacher_session(teacher_username)
    clean_payload = _validate_announcement_payload(payload)

    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": clean_payload}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement updated"}


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str, teacher_username: Optional[str] = None) -> Dict[str, str]:
    """Delete an announcement (requires authentication)."""
    _validate_teacher_session(teacher_username)

    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}
