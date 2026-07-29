from app.db.base import Base
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID,JSONB
from uuid import uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.documents import Document
    from app.models.tasks import Task 
    #from app.reminders.models import Reminder

class Opportunity(Base):
    __tablename__="opportunities"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid4)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"),nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    title: Mapped[str] = mapped_column(String(255),nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    priority: Mapped[str] = mapped_column(String(20),default="Medium")
    deadline: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30),default="Pending")
    required_documents: Mapped[list[str]] = mapped_column(JSONB,default=list)
    user: Mapped["User"] = relationship(back_populates="opportunities")
    document: Mapped["Document"] = relationship(back_populates="opportunities")
    tasks: Mapped[list["Task"]] = relationship(back_populates="opportunity",cascade="all, delete-orphan")
    #reminders: Mapped[list["Reminder"]] = relationship(back_populates="opportunity",cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"Opportunity("
            f"id={self.id}, "
            f"title={self.title!r}, "
            f"priority={self.priority!r}, "
            f"deadline={self.deadline})"
        )