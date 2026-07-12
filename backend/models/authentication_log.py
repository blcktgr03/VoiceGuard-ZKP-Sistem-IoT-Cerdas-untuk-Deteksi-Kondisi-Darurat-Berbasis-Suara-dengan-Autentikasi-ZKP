from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class AuthenticationLog(TimestampMixin, Base):
    """Audit log for Schnorr authentication attempts."""

    __tablename__ = "authentication_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), nullable=True)
    commitment: Mapped[str] = mapped_column(Text, nullable=False)
    challenge: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)

    device: Mapped["Device | None"] = relationship(back_populates="authentication_logs")
