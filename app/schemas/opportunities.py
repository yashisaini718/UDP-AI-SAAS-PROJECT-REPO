from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.tasks import TaskResponse

class OpportunityResponse(BaseModel):
    id: UUID
    title: str
    summary: str | None
    category: str | None
    priority: str
    deadline: datetime | None
    required_documents: list[str]
    tasks: list[TaskResponse]

    model_config = {
        "from_attributes": True
    }