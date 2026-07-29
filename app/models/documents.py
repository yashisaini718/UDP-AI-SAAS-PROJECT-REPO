from app.db.base import Base
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.opportunities import Opportunity

class Document(Base):
    __tablename__="documents"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    filename: Mapped[str] = mapped_column(String(255),nullable=False)
    file_path: Mapped[str] = mapped_column(String(500),nullable=False)
    file_type: Mapped[str] = mapped_column(String(30),nullable=False)
    file_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(UTC))
    user: Mapped["User"] = relationship(back_populates="documents")
    opportunities: Mapped[list["Opportunity"]] = relationship(back_populates="document",cascade="all, delete-orphan")