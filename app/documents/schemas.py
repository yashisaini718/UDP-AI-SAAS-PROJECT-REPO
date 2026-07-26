from pydantic import BaseModel
from uuid import UUID
from app.opportunity.schemas import OpportunityResponse
from app.tasks.schemas import TaskResponse


class UploadResponse(BaseModel):
    document_id: UUID
    opportunity: OpportunityResponse
    tasks: list[TaskResponse]