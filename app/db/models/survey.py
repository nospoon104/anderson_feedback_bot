from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Survey(Base):
    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"), nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    visit_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    table_number: Mapped[int] = mapped_column(Integer, nullable=False)

    q1: Mapped[bool] = mapped_column(Boolean, nullable=False)
    q2: Mapped[bool] = mapped_column(Boolean, nullable=False)
    q3: Mapped[bool] = mapped_column(Boolean, nullable=False)
    q4: Mapped[bool] = mapped_column(Boolean, nullable=False)

    comment_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    cafe: Mapped["Cafe"] = relationship(back_populates="surveys")
    created_by_user: Mapped["User"] = relationship(back_populates="surveys")
