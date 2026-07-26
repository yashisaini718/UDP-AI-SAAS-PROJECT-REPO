from app.db.base import Base
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.opportunity.models import Opportunity

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid4)
    opportunity_id: Mapped[UUID] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"),nullable=False)
    title: Mapped[str] = mapped_column(String(255),nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20),default="Medium")
    completed: Mapped[bool] = mapped_column(Boolean,default=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime)
    opportunity: Mapped["Opportunity"] = relationship(back_populates="tasks")
    
    def __repr__(self):
        return (
            f"Task("
            f"id={self.id}, "
            f"title={self.title!r}, "
            f"priority={self.priority!r}, "
            f"due_date={self.due_date})"
        )