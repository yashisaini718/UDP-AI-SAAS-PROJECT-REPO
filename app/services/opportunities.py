from fastapi import HTTPException, status, Request
from app.core.security import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import  selectinload
from sqlalchemy import select
from datetime import datetime
from app.models.users import User
from app.models.documents import Document
from app.models.opportunities import Opportunity
from app.models.tasks import Task

async def save_opportunity(db: AsyncSession, extracted_data: dict, document: Document)-> Opportunity:
    data = extracted_data

    deadline = None

    if data.get("deadline"):
        deadline = datetime.fromisoformat(data["deadline"])

    opportunity = Opportunity(
        document_id= document.id,
        user_id= document.user_id,
        title= data["title"],
        summary= data.get("summary"),
        description= data.get("description"),
        category= data.get("category"),
        priority= data.get("priority", "Medium"),
        deadline= deadline,
        required_documents= data.get("required_documents", []),
    )
    
    try:
        db.add(opportunity)

        await db.flush() # generate uuid

        for item in data.get("action_items", []):
            task_due_date = None

            if item.get("due_date"):
                task_due_date = datetime.fromisoformat(item["due_date"])

            task = Task(
                opportunity_id= opportunity.id,
                title= item["title"],
                description= item.get("description"),
                priority= item.get("priority", "Medium"),
                due_date= task_due_date,
            )
            db.add(task)
            
        return opportunity
    
    except Exception:
        db.rollback()

        raise


async def getall(db: AsyncSession):
    results= await db.execute(select(Opportunity).options(
            selectinload(Opportunity.tasks)
        ))
    return results.scalars().all()

async def getbydoc(doc_id: str, db: AsyncSession):
    result= await db.execute(
        select(Opportunity).options(
            selectinload(Opportunity.tasks)
        ).where(Opportunity.document_id == doc_id))
    return result.scalars().all()


async def getbyid(opp_id: str,db: AsyncSession):
    result= await db.execute(select(Opportunity).options(
            selectinload(Opportunity.tasks)
        ).where(Opportunity.id== opp_id))
    return result.scalars().all()