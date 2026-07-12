from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class Transcript(TimestampMixin, Base):
    """Whisper transcript associated with one audio upload."""

    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    audio_record_id: Mapped[int] = mapped_column(ForeignKey("audio_records.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    engine: Mapped[str] = mapped_column(String(120), nullable=False)

    audio_record: Mapped["AudioRecord"] = relationship(back_populates="transcript")
    classification: Mapped["Classification | None"] = relationship(
        back_populates="transcript",
        cascade="all, delete-orphan",
        uselist=False,
    )
