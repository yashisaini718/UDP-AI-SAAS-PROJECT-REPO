from pydantic import BaseModel
from uuid import UUID
from app.schemas.opportunities import OpportunityResponse
from app.schemas.tasks import TaskResponse


class UploadResponse(BaseModel):
    document_id: UUID
    file_name: str

class DocumentUploadResponse(BaseModel):
    message: str
    document: UploadResponse