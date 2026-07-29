from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import shutil
import hashlib
from app.models.documents import Document
from app.schemas.document import UploadResponse

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def save_file(file):
    path = UPLOAD_DIR / file.filename
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return str(path)


def calculate_file_hash(file):
    hasher = hashlib.sha256()

    while chunk := file.file.read(8192):
        hasher.update(chunk)

    file.file.seek(0)

    return hasher.hexdigest()


async def upload_document(db:AsyncSession , file, user):
    file_hash = calculate_file_hash(file)

    result = await db.execute(select(Document).where(Document.file_hash == file_hash))

    existing_document = result.scalar_one_or_none()

    if existing_document:
        return UploadResponse(
            document_id=existing_document.id,
            file_name=existing_document.filename
        )
    
    path= save_file(file)

    document= Document(
        filename=file.filename, 
        file_path=path, 
        file_type=file.content_type, 
        user_id=user.id,
        file_hash=file_hash
    )

    print ("Processing Document")

    db.add(document)

    await db.commit()

    await db.flush()

    return UploadResponse(
        document_id=document.id, 
        file_name=document.filename
    )

    