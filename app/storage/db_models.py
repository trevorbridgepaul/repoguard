"""
SQLAlchemy ORM models for scan persistence.

These are persistence-layer representations, distinct from the plain
dataclasses in app/domain/models.py — the domain layer doesn't know
about SQLAlchemy, and this layer doesn't know about FastAPI/Pydantic.
Conversion between the two happens in app/storage/db.py.

Two normalized tables (not a single JSONB blob) so the schema mirrors
the existing ScanResult/Finding relationship directly.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.domain.enums import ScanStatus, Severity


class Base(DeclarativeBase):
    pass


class ScanRecord(Base):
    __tablename__ = "scans"

    scan_id: Mapped[str] = mapped_column(String, primary_key=True)
    repo_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ScanStatus] = mapped_column(SqlEnum(ScanStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    findings: Mapped[list["FindingRecord"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        order_by="FindingRecord.id",
    )


class FindingRecord(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[str] = mapped_column(
        String, ForeignKey("scans.scan_id"), nullable=False
    )
    policy_id: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(SqlEnum(Severity), nullable=False)
    line: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    scan: Mapped["ScanRecord"] = relationship(back_populates="findings")
