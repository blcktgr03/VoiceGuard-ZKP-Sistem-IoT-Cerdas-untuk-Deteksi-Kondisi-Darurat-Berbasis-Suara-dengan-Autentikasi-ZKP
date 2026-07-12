from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class Classification(TimestampMixin, Base):
    """BERT classification result for one transcript."""

    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transcript_id: Mapped[int] = mapped_column(ForeignKey("transcripts.id"), nullable=False)
    label: Mapped[str] = mapped_column(String(30), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)

    transcript: Mapped["Transcript"] = relationship(back_populates="classification")
    notification: Mapped["Notification | None"] = relationship(
        back_populates="classification",
        cascade="all, delete-orphan",
        uselist=False,
    )
