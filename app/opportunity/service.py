from app.rag.prompts import PromptManager
from app.rag.llm import get_llm
from sqlalchemy.ext.asyncio import AsyncSession
import json
from datetime import datetime
from app.documents.models import Document
from app.opportunity.models import Opportunity
from app.tasks.models import Task

async def save_opportunity(db:AsyncSession, extracted_json:str, document:Document)->Opportunity:
    print(repr(extracted_json))
    data=json.loads(extracted_json)

    deadline=None
    if data.get("deadline"):
        deadline = datetime.fromisoformat(data["deadline"])

    opportunity = Opportunity(
        document_id=document.id,
        user_id=document.user_id,
        title=data["title"],
        summary=data.get("summary"),
        description=data.get("description"),
        category=data.get("category"),
        priority=data.get("priority", "Medium"),
        deadline=deadline,
        required_documents=data.get("required_documents", []),
    )
    try:
        db.add(opportunity)
        await db.flush() # generate uuid

        for item in data.get("action_items", []):
            task_due_date = None

            if item.get("due_date"):
                task_due_date = datetime.fromisoformat(item["due_date"])

            task = Task(
                opportunity_id=opportunity.id,
                title=item["title"],
                description=item.get("description"),
                priority=item.get("priority", "Medium"),
                due_date=task_due_date,
            )
            db.add(task)

        await db.commit()

        return opportunity
    
    except Exception:
        db.rollback()
        raise