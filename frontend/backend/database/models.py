"""SQLAlchemy ORM models for RegLoop AI database."""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum as PyEnum

Base = declarative_base()


class DocumentType(str, PyEnum):
    """Enum for document types."""
    REGULATION = "regulation"
    POLICY = "policy"
    COMPLIANCE = "compliance"
    OTHER = "other"


class ObligationCategory(str, PyEnum):
    """Enum for obligation categories."""
    OPERATIONAL = "operational"
    REPORTING = "reporting"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class PriorityLevel(str, PyEnum):
    """Enum for priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GapStatus(str, PyEnum):
    """Enum for gap analysis status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    MITIGATED = "mitigated"


class Document(Base):
    """Document model - stores uploaded regulatory documents."""
    
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    document_type = Column(SQLEnum(DocumentType), default=DocumentType.OTHER)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    text_length = Column(Integer, default=0)
    raw_text = Column(Text, nullable=True)

    # Relationships
    obligations = relationship(
        "Obligation",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    # Indexes
    __table_args__ = (
        Index("ix_documents_filename_type", "filename", "document_type"),
        Index("ix_documents_uploaded_at", "uploaded_at"),
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename='{self.filename}', type={self.document_type})>"


class Obligation(Base):
    """Obligation model - stores extracted regulatory obligations."""
    
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    obligation_id = Column(String(100), nullable=False, index=True)  # External ID from Claude
    obligation_text = Column(Text, nullable=False)
    category = Column(SQLEnum(ObligationCategory), default=ObligationCategory.COMPLIANCE)
    priority = Column(SQLEnum(PriorityLevel), default=PriorityLevel.MEDIUM)
    responsible_team = Column(String(255), nullable=True)
    evidence_required = Column(Text, nullable=True)
    deadline_or_frequency = Column(String(255), nullable=True)
    risk_if_not_met = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="obligations")
    gap_analysis = relationship(
        "GapAnalysis",
        back_populates="obligation",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_obligations_document_id", "document_id"),
        Index("ix_obligations_category_priority", "category", "priority"),
        Index("ix_obligations_obligation_id", "obligation_id"),
    )

    def __repr__(self) -> str:
        return f"<Obligation(id={self.id}, obligation_id='{self.obligation_id}', category={self.category})>"


class GapAnalysis(Base):
    """Gap Analysis model - tracks compliance gaps and remediation."""
    
    __tablename__ = "gap_analysis"

    id = Column(Integer, primary_key=True, index=True)
    obligation_id = Column(Integer, ForeignKey("obligations.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum(GapStatus), default=GapStatus.OPEN)
    coverage_score = Column(Float, default=0.0)  # 0.0 to 100.0
    gap_summary = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    obligation = relationship("Obligation", back_populates="gap_analysis")

    # Indexes
    __table_args__ = (
        Index("ix_gap_analysis_obligation_id", "obligation_id"),
        Index("ix_gap_analysis_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<GapAnalysis(id={self.id}, status={self.status}, coverage_score={self.coverage_score})>"
