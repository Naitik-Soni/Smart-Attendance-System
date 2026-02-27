import base64
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


async def recognize_faces(source_type: str, source_id: str, timestamp: datetime, image: UploadFile) -> dict:
    img_content = await image.read()
    encoded = base64.b64encode(img_content).decode("utf-8")
    content_type = image.content_type or "application/octet-stream"

    payload = {
        "source_type": source_type,
        "source_id": source_id,
        "timestamp": timestamp.isoformat(),
        "image": f"data:{content_type};base64,{encoded}",
    }
    url = f"{settings.FACE_SERVICE_URL}/v1/faces/recognize"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.is_success:
                return resp.json()
            return _error_payload(resp)
    except Exception as exc:
        return {"error": {"status_code": 503, "body": {"detail": str(exc)}}}


async def register_faces(user_id: str, files: list[UploadFile]) -> dict:
    url = f"{settings.FACE_SERVICE_URL}/v1/faces/register"
    upload_files = []
    for file in files:
        content = await file.read()
        upload_files.append(("images", (file.filename, content, file.content_type)))

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, data={"user_id": user_id}, files=upload_files)
            if resp.is_success:
                return resp.json()
            return _error_payload(resp)
    except Exception as exc:
        return {"error": {"status_code": 503, "body": {"detail": str(exc)}}}


async def delete_face(face_id: str) -> dict:
    url = f"{settings.FACE_SERVICE_URL}/v1/faces/{face_id}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.delete(url)
            if resp.is_success:
                return resp.json()
            return _error_payload(resp)
    except Exception as exc:
        return {"error": {"status_code": 503, "body": {"detail": str(exc)}}}
