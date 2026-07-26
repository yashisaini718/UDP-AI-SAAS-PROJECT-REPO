from app.db.base import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.opportunity.models import Opportunity

class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid4)
    opportunity_id: Mapped[UUID] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"),nullable=False)
    remind_at: Mapped[datetime] = mapped_column(DateTime,nullable=False)
    message: Mapped[str] = mapped_column(Text,nullable=False)
    sent: Mapped[bool] = mapped_column(Boolean,default=False)
    opportunity: Mapped["Opportunity"] = relationship(back_populates="reminders")