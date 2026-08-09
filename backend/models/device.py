from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin


class Device(TimestampMixin, Base):
    """Registered IoT device and Schnorr public key."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    public_key: Mapped[str] = mapped_column(String(512), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)

    authentication_logs: Mapped[list["AuthenticationLog"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
    )
    authentication_challenges: Mapped[list["AuthenticationChallenge"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
    )
    audio_records: Mapped[list["AudioRecord"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
    )
