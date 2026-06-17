"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ============================================================================
# Document Schemas
# ============================================================================

class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str
    document_type: str = "other"
    text_length: int = 0


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    raw_text: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Schema for document API response."""
    id: int
    uploaded_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Obligation Schemas
# ============================================================================

class ObligationBase(BaseModel):
    """Base obligation schema."""
    obligation_id: str
    obligation_text: str
    category: str = "other"
    priority: str = "medium"
    responsible_team: Optional[str] = None
    evidence_required: Optional[str] = None
    deadline_or_frequency: Optional[str] = None
    risk_if_not_met: Optional[str] = None


class ObligationCreate(ObligationBase):
    """Schema for creating an obligation."""
    document_id: int


class ObligationResponse(ObligationBase):
    """Schema for obligation API response."""
    id: int
    document_id: int
    created_at: datetime
    gap_analysis: Optional['GapAnalysisResponse'] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Gap Analysis Schemas
# ============================================================================

class GapAnalysisBase(BaseModel):
    """Base gap analysis schema."""
    status: str = "open"
    coverage_score: float = 0.0
    gap_summary: Optional[str] = None
    recommended_action: Optional[str] = None


class GapAnalysisCreate(GapAnalysisBase):
    """Schema for creating gap analysis."""
    obligation_id: int


class GapAnalysisResponse(GapAnalysisBase):
    """Schema for gap analysis API response."""
    id: int
    obligation_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Composite Schemas
# ============================================================================

class DocumentWithObligations(DocumentResponse):
    """Document with all related obligations."""
    obligations: List[ObligationResponse] = []


class ObligationWithGapAnalysis(ObligationResponse):
    """Obligation with gap analysis details."""
    gap_analysis: Optional[GapAnalysisResponse] = None


# Update forward refs
ObligationResponse.model_rebuild()
