from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.face import RecognizeRequest
from app.services import embedding_store, id_map_store, matcher
from app.services.recognition_service import recognize
from app.services.registration_service import delete_face as delete_face_service
from app.services.registration_service import register_faces as register_faces_service


router = APIRouter(prefix="/faces", tags=["Faces"])


@router.post("/register")
async def register_faces(
    user_id: str = Form(...),
    images: list[UploadFile] = File(...),
):
    data = register_faces_service(user_id=user_id, images=images, store=embedding_store, id_map=id_map_store)

    return {
        "success": True,
        "code": "FACE_REGISTERED",
        "message": "Face registered successfully",
        "data": data,
        "meta": {"images_received": len(images)},
        "errors": [],
    }


@router.post("/recognize")
def recognize_faces(payload: RecognizeRequest):
    response = recognize(payload, matcher)
    return {
        "success": True,
        "code": "FACE_RECOGNIZED",
        "message": "Recognition completed",
        "data": response.model_dump(),
        "meta": {"source_id": payload.source_id},
        "errors": [],
    }


@router.delete("/{face_id}")
def delete_face(face_id: str):
    data = delete_face_service(face_id, embedding_store, id_map_store)
    return {
        "success": True,
        "code": "FACE_DELETED",
        "message": "Face deleted successfully",
        "data": data,
        "meta": {},
        "errors": [],
    }
