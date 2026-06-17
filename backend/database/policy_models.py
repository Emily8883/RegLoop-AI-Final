"""PolicyPullRequest and ReviewAction models for RegLoop AI"""

from datetime import datetime
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
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from database.models import Base


class ReviewStatus(str, PyEnum):
    """Enum for policy PR review status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    ESCALATED = "escalated"


class ReviewAction(str, PyEnum):
    """Enum for reviewer actions."""
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    ESCALATE = "escalate"
    REQUEST_INFO = "request_info"


class PolicyPullRequest(Base):
    """Policy Pull Request model - proposed policy amendments based on gaps"""
    
    __tablename__ = "policy_pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    gap_analysis_id = Column(Integer, ForeignKey("gap_analysis.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Amendment details
    original_policy_text = Column(Text, nullable=True)  # Original policy section
    proposed_amendment = Column(Text, nullable=False)  # Suggested change
    regulatory_citation = Column(String(500), nullable=False)  # Reference to regulation
    
    # Amendment metadata
    gap_description = Column(Text, nullable=False)  # Why amendment is needed
    suggested_owner = Column(String(255), nullable=True)  # Who should implement
    risk_level = Column(String(50), nullable=False)  # high, medium, low
    confidence_score = Column(Float, default=0.75)  # 0.0-1.0
    
    # Amendment tracking
    before_text = Column(Text, nullable=True)  # Before text for diff
    after_text = Column(Text, nullable=True)  # After text for diff
    diff_summary = Column(Text, nullable=True)  # Human-readable diff
    
    # Status tracking
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    gap_analysis = relationship("GapAnalysis")
    review_actions = relationship(
        "PolicyReviewAction",
        back_populates="policy_pr",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    # Indexes
    __table_args__ = (
        Index("ix_policy_prs_status", "status"),
        Index("ix_policy_prs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<PolicyPullRequest(id={self.id}, gap_id={self.gap_analysis_id}, status={self.status})>"


class PolicyReviewAction(Base):
    """PolicyReviewAction model - tracks human review decisions"""
    
    __tablename__ = "policy_review_actions"

    id = Column(Integer, primary_key=True, index=True)
    policy_pr_id = Column(Integer, ForeignKey("policy_pull_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Review details
    reviewer_name = Column(String(255), nullable=True)  # Person doing review
    action = Column(SQLEnum(ReviewAction), nullable=False)  # approve/reject/modify/escalate
    comments = Column(Text, nullable=True)  # Reviewer comments
    suggested_modifications = Column(Text, nullable=True)  # If modifying, what changes
    
    # Action tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    policy_pr = relationship("PolicyPullRequest", back_populates="review_actions")

    # Indexes
    __table_args__ = (
        Index("ix_policy_review_actions_action", "action"),
        Index("ix_policy_review_actions_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<PolicyReviewAction(id={self.id}, pr_id={self.policy_pr_id}, action={self.action})>"
