import hashlib
from http import HTTPStatus
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse


from dfapp.api.v1.schemas import UploadFileResponse
from dfapp.services.auth.utils import get_current_active_user
from dfapp.services.database.models.flow import Flow
from dfapp.services.deps import get_session, get_storage_service
from dfapp.services.storage.service import StorageService
from dfapp.services.storage.utils import build_content_type_from_extension

router = APIRouter(tags=["Files"], prefix="/files")


# Create dep that gets the flow_id from the request
# then finds it in the database and returns it while
# using the current user as the owner
def get_flow_id(
    flow_id: str,
    current_user=Depends(get_current_active_user),
    session=Depends(get_session),
):
    # AttributeError: 'SelectOfScalar' object has no attribute 'first'
    flow = session.get(Flow, flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    if flow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have access to this flow")
    return flow_id


@router.post("/upload/{flow_id}", status_code=HTTPStatus.CREATED)
async def upload_file(
    file: UploadFile,
    flow_id: str = Depends(get_flow_id),
    storage_service: StorageService = Depends(get_storage_service),
):
    try:
        file_content = await file.read()
        file_name = file.filename or hashlib.sha256(file_content).hexdigest()
        folder = flow_id
        await storage_service.save_file(flow_id=folder, file_name=file_name, data=file_content)
        return UploadFileResponse(flowId=flow_id, file_path=f"{folder}/{file_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{flow_id}/{file_name}")
async def download_file(file_name: str, flow_id: str, storage_service: StorageService = Depends(get_storage_service)):
    try:
        extension = file_name.split(".")[-1]

        if not extension:
            raise HTTPException(status_code=500, detail=f"Extension not found for file {file_name}")

        content_type = build_content_type_from_extension(extension)

        if not content_type:
            raise HTTPException(status_code=500, detail=f"Content type not found for extension {extension}")

        file_content = await storage_service.get_file(flow_id=flow_id, file_name=file_name)
        headers = {
            "Content-Disposition": f"attachment; filename={file_name} filename*=UTF-8''{file_name}",
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(file_content)),
        }
        return StreamingResponse(BytesIO(file_content), media_type=content_type, headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{flow_id}/{file_name}")
async def download_image(file_name: str, flow_id: str, storage_service: StorageService = Depends(get_storage_service)):
    try:
        extension = file_name.split(".")[-1]

        if not extension:
            raise HTTPException(status_code=500, detail=f"Extension not found for file {file_name}")

        content_type = build_content_type_from_extension(extension)

        if not content_type:
            raise HTTPException(status_code=500, detail=f"Content type not found for extension {extension}")
        elif not content_type.startswith("image"):
            raise HTTPException(status_code=500, detail=f"Content type {content_type} is not an image")

        file_content = await storage_service.get_file(flow_id=flow_id, file_name=file_name)
        return StreamingResponse(BytesIO(file_content), media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{flow_id}")
async def list_files(
    flow_id: str = Depends(get_flow_id), storage_service: StorageService = Depends(get_storage_service)
):
    try:
        files = await storage_service.list_files(flow_id=flow_id)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{flow_id}/{file_name}")
async def delete_file(
    file_name: str, flow_id: str = Depends(get_flow_id), storage_service: StorageService = Depends(get_storage_service)
):
    try:
        await storage_service.delete_file(flow_id=flow_id, file_name=file_name)
        return {"message": f"File {file_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
