from __future__ import annotations

from postgrest.exceptions import APIError

from app.db import get_supabase
from app.db.supabase_errors import is_missing_table_error
from app.db.supabase_response import response_data


class ContactRepository:
    def __init__(self) -> None:
        self.client = get_supabase()

    def create(
        self,
        *,
        name: str,
        email: str,
        subject: str,
        message: str,
        category: str,
        user_id: str | None = None,
    ) -> dict:
        row = {
            "name": name.strip(),
            "email": email.strip().lower(),
            "subject": subject.strip(),
            "message": message.strip(),
            "category": category,
            "user_id": user_id,
            "status": "new",
        }
        try:
            result = self.client.table("contact_submissions").insert(row).execute()
        except APIError as exc:
            if is_missing_table_error(exc, "contact_submissions"):
                raise RuntimeError("contact_table_missing") from exc
            raise
        data = response_data(result)
        if isinstance(data, list):
            return data[0] if data else row
        return data or row

    def list_all(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> list[dict]:
        end = offset + limit - 1
        query = (
            self.client.table("contact_submissions")
            .select("*")
            .order("created_at", desc=True)
        )
        if status:
            query = query.eq("status", status)
        try:
            result = query.range(offset, end).execute()
        except APIError as exc:
            if is_missing_table_error(exc, "contact_submissions"):
                return []
            raise
        return list(response_data(result) or [])

    def update_status(self, submission_id: str, status: str) -> dict | None:
        try:
            result = (
                self.client.table("contact_submissions")
                .update({"status": status})
                .eq("id", submission_id)
                .execute()
            )
        except APIError as exc:
            if is_missing_table_error(exc, "contact_submissions"):
                return None
            raise
        data = response_data(result)
        if isinstance(data, list):
            return data[0] if data else None
        return data
