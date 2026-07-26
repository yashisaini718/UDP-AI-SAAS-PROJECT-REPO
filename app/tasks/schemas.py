from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    priority: str
    due_date: datetime | None

    model_config = {
        "from_attributes": True
    }