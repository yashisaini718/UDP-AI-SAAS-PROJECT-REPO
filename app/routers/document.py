from fastapi import APIRouter, Depends, UploadFile
from app.db.session import AsyncSession, get_db
from app.core.security import get_current_user
from app.services.document import upload_document
from app.schemas.document import DocumentUploadResponse


router=APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload-document",response_model=DocumentUploadResponse)
async def upload(
    file: UploadFile,
    db: AsyncSession=Depends(get_db), 
    current_user=Depends(get_current_user)
):

    return await upload_document(db, file, current_user)

