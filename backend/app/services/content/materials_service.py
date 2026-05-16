from __future__ import annotations

import logging
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.config import get_settings
from app.models.material import MaterialPublic
from app.services.content.content_type import is_allowed_material_type, resolve_content_type
from app.services.content.ingestion import extract_text_from_bytes
from app.services.content.materials_repository import MaterialsRepository

logger = logging.getLogger(__name__)

MAX_BYTES = 10 * 1024 * 1024


class MaterialsService:
    def __init__(self) -> None:
        self.repo = MaterialsRepository()
        self.settings = get_settings()

    def _material_file_url(self, material_id: str) -> str:
        base = self.settings.api_public_url.rstrip("/")
        return f"{base}/content/materials/{material_id}/file"

    def list_materials(self, user_id: str) -> list[MaterialPublic]:
        rows = self.repo.list_for_user(user_id)
        return [MaterialPublic.model_validate(r) for r in rows]

    async def _extract_and_store(self, mid: str, data: bytes, content_type: str, file_url: str) -> dict:
        row = self.repo.get_by_id(mid) or {}
        try:
            extracted = await extract_text_from_bytes(
                data,
                content_type,
                settings=self.settings,
                file_url=file_url,
            )
            if extracted.strip():
                return self.repo.update_extracted_text(mid, extracted[:50000])
        except Exception as exc:
            logger.warning("Text extraction failed for material %s: %s", mid, exc)
        return row

    async def upload_material(self, user_id: str, file: UploadFile) -> MaterialPublic:
        filename = file.filename or "upload"
        raw_type = file.content_type or ""
        content_type = resolve_content_type(filename, raw_type)

        if not is_allowed_material_type(raw_type, filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Allowed: PDF, plain text, markdown, code/text files, JPEG, PNG, WebP, GIF",
            )

        data = await file.read()
        if len(data) > MAX_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Max file size is 10 MB",
            )

        row = self.repo.create_with_file(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            file_bytes=data,
        )
        mid = str(row["id"])
        file_url = self._material_file_url(mid)
        row = self.repo.set_file_url(mid, file_url)
        row = await self._extract_and_store(mid, data, content_type, file_url)

        return MaterialPublic.model_validate(row)

    async def ensure_material_text(self, user_id: str, material_id: str) -> str:
        """Return extracted text, re-reading the file from disk if needed."""
        row = self.repo.get_by_id(material_id)
        if not row or str(row["user_id"]) != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

        text = (row.get("extracted_text") or "").strip()
        if text:
            return text

        path = self.repo.file_path(material_id)
        if not path or not path.is_file():
            return ""

        data = path.read_bytes()
        content_type = resolve_content_type(
            str(row.get("filename") or ""),
            str(row.get("content_type") or ""),
        )
        file_url = str(row.get("file_url") or self._material_file_url(material_id))

        try:
            extracted = await extract_text_from_bytes(
                data,
                content_type,
                settings=self.settings,
                file_url=file_url,
            )
            if extracted.strip():
                self.repo.update_extracted_text(material_id, extracted[:50000])
                return extracted.strip()
        except Exception as exc:
            logger.warning("Re-extraction failed for material %s: %s", material_id, exc)

        return ""

    def get_material_text(self, user_id: str, material_id: str) -> str:
        row = self.repo.get_by_id(material_id)
        if not row or str(row["user_id"]) != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
        return (row.get("extracted_text") or "").strip()

    def get_material_file_response(self, user_id: str, material_id: str) -> FileResponse:
        row = self.repo.get_by_id(material_id)
        if not row or str(row["user_id"]) != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
        path = self.repo.file_path(material_id)
        if not path or not path.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        media = row.get("content_type") or "application/octet-stream"
        filename = Path(row.get("filename") or "download").name
        return FileResponse(path, media_type=media, filename=filename)

    def delete_material(self, user_id: str, material_id: str) -> None:
        row = self.repo.get_by_id(material_id)
        if not row or str(row["user_id"]) != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
        self.repo.delete(material_id)
