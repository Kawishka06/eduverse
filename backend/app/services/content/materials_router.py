from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse

from app.core.dependencies import get_current_user_id
from app.models.material import MaterialPublic
from app.services.content.materials_service import MaterialsService

router = APIRouter(prefix="/content", tags=["content"])


def get_materials_service() -> MaterialsService:
    return MaterialsService()


@router.get("/materials", response_model=list[MaterialPublic])
def list_materials(
    user_id: str = Depends(get_current_user_id),
    service: MaterialsService = Depends(get_materials_service),
) -> list[MaterialPublic]:
    return service.list_materials(user_id)


@router.post("/materials", response_model=MaterialPublic, status_code=status.HTTP_201_CREATED)
async def upload_material(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    service: MaterialsService = Depends(get_materials_service),
) -> MaterialPublic:
    return await service.upload_material(user_id, file)


@router.get("/materials/{material_id}/file")
def download_material_file(
    material_id: str,
    user_id: str = Depends(get_current_user_id),
    service: MaterialsService = Depends(get_materials_service),
) -> FileResponse:
    return service.get_material_file_response(user_id, material_id)


@router.delete("/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: str,
    user_id: str = Depends(get_current_user_id),
    service: MaterialsService = Depends(get_materials_service),
) -> None:
    service.delete_material(user_id, material_id)
