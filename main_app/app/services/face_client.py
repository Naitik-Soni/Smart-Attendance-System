import base64
import json
from datetime import datetime

import httpx
from fastapi import UploadFile

from ..core.config import settings


def _error_payload(resp: httpx.Response) -> dict:
    try:
        body = resp.json()
    except Exception:
        body = {"detail": resp.text}
    return {"error": {"status_code": resp.status_code, "body": body}}


async def recognize_faces(
    source_type: str,
    source_id: str,
    timestamp: datetime,
    image: UploadFile,
    policies: dict | None = None,
) -> dict:
    img_content = await image.read()
    encoded = base64.b64encode(img_content).decode("utf-8")
    content_type = image.content_type or "application/octet-stream"

    payload = {
        "source_type": source_type,
        "source_id": source_id,
        "timestamp": timestamp.isoformat(),
        "image": f"data:{content_type};base64,{encoded}",
        "policy": policies or {},
    }
    url = f"{settings.FACE_SERVICE_URL}/faces/recognize"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            if resp.is_success:
                return resp.json()
            return _error_payload(resp)
    except Exception as exc:
        return {"error": {"status_code": 503, "body": {"detail": str(exc)}}}


async def register_faces(user_id: str, files: list[UploadFile], policies: dict | None = None) -> dict:
    url = f"{settings.FACE_SERVICE_URL}/faces/register"
    upload_files = []
    for file in files:
        content = await file.read()
        upload_files.append(("images", (file.filename, content, file.content_type)))

    try:
        # Enrollment can be slower on first model load / heavier image sets.
        async with httpx.AsyncClient(timeout=120.0) as client:
            data = {"user_id": user_id}
            if policies:
                data["policy_json"] = json.dumps(policies)
            resp = await client.post(url, data=data, files=upload_files)
            if resp.is_success:
                return resp.json()
            return _error_payload(resp)
    except Exception as exc:
        return {"error": {"status_code": 503, "body": {"detail": str(exc)}}}


async def delete_face(face_id: str) -> dict:
    url = f"{settings.FACE_SERVICE_URL}/faces/{face_id}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.delete(url)
            if resp.is_success:
                return resp.json()
            return _error_payload(resp)
    except Exception as exc:
        return {"error": {"status_code": 503, "body": {"detail": str(exc)}}}
