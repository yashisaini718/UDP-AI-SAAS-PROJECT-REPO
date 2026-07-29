#all sqlalchemy models
from app.db.base import Base
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, DateTime
from app.models.opportunities import Opportunity
from sqlalchemy.dialects.postgresql import UUID
from app.models.documents import Document 
from uuid import uuid4

class User(Base):
    __tablename__="users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid4)
    username: Mapped[str] = mapped_column(String(100),nullable=False)
    email: Mapped[str] = mapped_column(String(255),unique=True,nullable=False)
    hashed_password: Mapped[str]=mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(UTC),onupdate=lambda: datetime.now(UTC))
    opportunities: Mapped[list["Opportunity"]] = relationship(back_populates="user",cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="user",cascade="all, delete-orphan")
