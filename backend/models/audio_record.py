from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class AudioRecord(TimestampMixin, Base):
    """Metadata for an uploaded audio file."""

    __tablename__ = "audio_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    device: Mapped["Device"] = relationship(back_populates="audio_records")
    transcript: Mapped["Transcript | None"] = relationship(
        back_populates="audio_record",
        cascade="all, delete-orphan",
        uselist=False,
    )
