from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class OpportunityResponse(BaseModel):
    id: UUID
    title: str
    summary: str | None
    category: str | None
    priority: str
    deadline: datetime | None

    model_config = {
        "from_attributes": True
    }