from app.rag.prompts import PromptManager
from app.rag.llm import get_llm
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import shutil
from app.documents.models import Document
from app.rag.ingestion import IngestionPipeline
from app.opportunity.service import save_opportunity

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def save_file(file):
    path = UPLOAD_DIR / file.filename
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return str(path)

async def extract_json(path):
    pages=IngestionPipeline.load_document(path)

    if not pages:
        print ("No document found.")

    text="\n".join(page.page_content for page in pages)

    llm=get_llm()
    prompt= PromptManager.extract_json_prompt(text=text)

    response=llm.invoke(prompt)

    return response.content


async def upload_document(db:AsyncSession , file, user):
    path= save_file(file)
    document= Document(filename=file.filename, file_path=path, file_type=file.content_type, user_id=user.id)
    print ("Processing Document")

    db.add(document)
    await db.commit()
    db.flush()

    opportunities= await extract_json(path)  
    await save_opportunity(db=db, extracted_json=opportunities, document=document)
    print ("Uploaded Document")