from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, EmailStr, Field

from app.core.dependencies import require_roles
from app.core.rate_limit import rate_limit_ip
from app.core.security import extract_bearer_token
from app.core.supabase_auth import claims_to_user_fields, validate_supabase_token
from app.models.enums import UserRole
from app.models.user import UserPublic
from app.debug_log import debug_log
from app.services.contact.repository import ContactRepository

router = APIRouter(tags=["contact"])


class ContactSubmissionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=10, max_length=5000)
    category: str = Field(
        default="general",
        pattern="^(general|support|billing|legal|dmca|other)$",
    )


class ContactSubmissionPublic(BaseModel):
    id: str
    message: str = "Thank you. We received your message and will respond soon."


class ContactSubmissionRow(BaseModel):
    id: str
    user_id: str | None
    name: str
    email: str
    subject: str
    category: str
    message: str
    status: str
    created_at: str


def _optional_user_id(request: Request) -> str | None:
    token = extract_bearer_token(request.headers.get("Authorization"))
    if not token:
        return None
    try:
        claims = validate_supabase_token(token)
        return claims_to_user_fields(claims)["id"]
    except ValueError:
        return None


@router.post("/contact", response_model=ContactSubmissionPublic, status_code=status.HTTP_201_CREATED)
def submit_contact(
    payload: ContactSubmissionCreate,
    request: Request,
    user_id: str | None = Depends(_optional_user_id),
) -> ContactSubmissionPublic:
    rate_limit_ip(request, limit=5, window_seconds=3600)

    # #region agent log
    debug_log(
        "contact/router.py:submit_contact",
        "submit_contact entry",
        {"category": payload.category, "hasUserId": user_id is not None},
        hypothesis_id="C3",
        run_id="post-fix",
    )
    # #endregion

    repo = ContactRepository()
    try:
        row = repo.create(
            name=payload.name,
            email=str(payload.email),
            subject=payload.subject,
            message=payload.message,
            category=payload.category,
            user_id=user_id,
        )
    except RuntimeError as exc:
        if str(exc) == "contact_table_missing":
            # #region agent log
            debug_log(
                "contact/router.py:submit_contact",
                "contact_table_missing",
                {},
                hypothesis_id="C1",
                run_id="post-fix",
            )
            # #endregion
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Contact form database table is missing. Run "
                    "supabase/migrations/010_contact_submissions.sql in the Supabase SQL Editor, "
                    "or set SUPABASE_DB_PASSWORD in backend/.env and restart the API."
                ),
            ) from exc
        raise

    # #region agent log
    debug_log(
        "contact/router.py:submit_contact",
        "contact submission created",
        {"submissionId": str(row.get("id", ""))[:8]},
        hypothesis_id="C3",
        run_id="post-fix",
    )
    # #endregion

    return ContactSubmissionPublic(id=str(row["id"]))


@router.get("/admin/contact-submissions", response_model=list[ContactSubmissionRow])
def list_contact_submissions(
    _admin: UserPublic = Depends(require_roles(UserRole.ADMIN.value)),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
) -> list[ContactSubmissionRow]:
    rows = ContactRepository().list_all(limit=limit, offset=offset, status=status)
    return [
        ContactSubmissionRow(
            id=str(r["id"]),
            user_id=str(r["user_id"]) if r.get("user_id") else None,
            name=r["name"],
            email=r["email"],
            subject=r["subject"],
            category=r.get("category") or "general",
            message=r["message"],
            status=r.get("status") or "new",
            created_at=str(r["created_at"]),
        )
        for r in rows
    ]


@router.patch("/admin/contact-submissions/{submission_id}")
def update_contact_status(
    submission_id: str,
    status_value: str = Query(alias="status", pattern="^(new|read|resolved)$"),
    _admin: UserPublic = Depends(require_roles(UserRole.ADMIN.value)),
) -> dict:
    row = ContactRepository().update_status(submission_id, status_value)
    if not row:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"id": submission_id, "status": status_value}
