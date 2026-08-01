from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.opportunities import OpportunityResponse
from app.models.users import User
from app.core.security import get_current_user
from app.services.opportunities import getall, getbydoc, getbyid


router=APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.get("/", response_model=list[OpportunityResponse])
async def get_all_opportunity(
    current_user= Depends(get_current_user), 
    db: AsyncSession= Depends(get_db)
):
    
    return await getall(db=db)

@router.get("/document/{doc_id}", response_model=list[OpportunityResponse])
async def get_opportunity_by_doc(
    doc_id: str, 
    current_user= Depends(get_current_user), 
    db: AsyncSession= Depends(get_db)
):
    
    return await getbydoc(doc_id=doc_id, db=db)


@router.get("/{opp_id}", response_model=list[OpportunityResponse])
async def get_opportunity_by_id(
    opp_id: str,
    current_user= Depends(get_current_user), 
    db: AsyncSession= Depends(get_db)
):
    
    return await getbyid(opp_id=opp_id, db=db)