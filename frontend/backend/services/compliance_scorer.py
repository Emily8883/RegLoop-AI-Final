"""Compliance coverage scoring service for RegLoop AI."""

from typing import Dict, List, Any
from sqlalchemy.orm import Session
from database.models import Obligation, PriorityLevel, ObligationCategory
import logging

logger = logging.getLogger(__name__)


class ComplianceCoverageScorer:
    """Calculates compliance coverage scores based on obligation priorities."""
    
    # Priority-based scoring rules (MVP)
    PRIORITY_SCORES = {
        PriorityLevel.HIGH: 90,
        PriorityLevel.MEDIUM: 70,
        PriorityLevel.LOW: 50,
    }
    
    @classmethod
    def get_score_for_priority(cls, priority: PriorityLevel) -> int:
        """Get coverage score for a priority level.
        
        Args:
            priority: PriorityLevel enum value
            
        Returns:
            Coverage score (50-90)
        """
        if isinstance(priority, str):
            priority = PriorityLevel(priority)
        
        return cls.PRIORITY_SCORES.get(priority, 50)
    
    @classmethod
    def calculate_obligation_coverage(cls, obligation: Obligation) -> int:
        """Calculate coverage score for a single obligation.
        
        Args:
            obligation: Obligation ORM object
            
        Returns:
            Coverage score based on priority (50-90)
        """
        return cls.get_score_for_priority(obligation.priority)
    
    @classmethod
    def calculate_category_coverage(
        cls, 
        db: Session, 
        category: ObligationCategory
    ) -> Dict[str, Any]:
        """Calculate average coverage for a specific category.
        
        Args:
            db: SQLAlchemy session
            category: ObligationCategory enum value
            
        Returns:
            Dictionary with category stats including average coverage
        """
        obligations = db.query(Obligation).filter(
            Obligation.category == category
        ).all()
        
        if not obligations:
            return {
                "category": category.value,
                "total_obligations": 0,
                "average_coverage": 0,
                "scores": []
            }
        
        scores = [cls.calculate_obligation_coverage(obl) for obl in obligations]
        average_coverage = sum(scores) / len(scores) if scores else 0
        
        return {
            "category": category.value,
            "total_obligations": len(obligations),
            "average_coverage": round(average_coverage, 1),
            "scores": scores
        }
    
    @classmethod
    def calculate_overall_compliance(cls, db: Session) -> Dict[str, Any]:
        """Calculate overall compliance coverage score.
        
        This calculates:
        1. Overall compliance score (average across all obligations)
        2. Coverage per category
        3. Priority breakdown
        
        Args:
            db: SQLAlchemy session
            
        Returns:
            Comprehensive compliance score report
        """
        # Get all obligations
        all_obligations = db.query(Obligation).all()
        
        if not all_obligations:
            return {
                "overall_compliance_score": 0,
                "total_obligations": 0,
                "categories": [],
                "priority_breakdown": {
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "high_coverage": 0,
                    "medium_coverage": 0,
                    "low_coverage": 0,
                }
            }
        
        # Calculate scores for all obligations
        all_scores = [
            cls.calculate_obligation_coverage(obl) 
            for obl in all_obligations
        ]
        overall_compliance_score = round(sum(all_scores) / len(all_scores), 1)
        
        # Calculate per-category coverage
        categories_data = []
        for category in ObligationCategory:
            category_info = cls.calculate_category_coverage(db, category)
            if category_info["total_obligations"] > 0:
                categories_data.append({
                    "category": category_info["category"],
                    "total_obligations": category_info["total_obligations"],
                    "average_coverage": category_info["average_coverage"],
                })
        
        # Calculate priority breakdown
        priority_stats = cls._calculate_priority_breakdown(db, all_obligations)
        
        return {
            "overall_compliance_score": overall_compliance_score,
            "total_obligations": len(all_obligations),
            "categories": categories_data,
            "priority_breakdown": priority_stats,
        }
    
    @classmethod
    def _calculate_priority_breakdown(
        cls, 
        db: Session, 
        obligations: List[Obligation]
    ) -> Dict[str, Any]:
        """Calculate breakdown by priority level.
        
        Args:
            db: SQLAlchemy session
            obligations: List of all obligations
            
        Returns:
            Dictionary with priority level statistics
        """
        high_count = sum(1 for obl in obligations if obl.priority == PriorityLevel.HIGH)
        medium_count = sum(1 for obl in obligations if obl.priority == PriorityLevel.MEDIUM)
        low_count = sum(1 for obl in obligations if obl.priority == PriorityLevel.LOW)
        
        total = len(obligations)
        
        # Calculate average coverage per priority level
        high_scores = [
            cls.PRIORITY_SCORES[PriorityLevel.HIGH] 
            for obl in obligations 
            if obl.priority == PriorityLevel.HIGH
        ]
        medium_scores = [
            cls.PRIORITY_SCORES[PriorityLevel.MEDIUM] 
            for obl in obligations 
            if obl.priority == PriorityLevel.MEDIUM
        ]
        low_scores = [
            cls.PRIORITY_SCORES[PriorityLevel.LOW] 
            for obl in obligations 
            if obl.priority == PriorityLevel.LOW
        ]
        
        return {
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "high_coverage": round(sum(high_scores) / len(high_scores), 1) if high_scores else 0,
            "medium_coverage": round(sum(medium_scores) / len(medium_scores), 1) if medium_scores else 0,
            "low_coverage": round(sum(low_scores) / len(low_scores), 1) if low_scores else 0,
        }
    
    @classmethod
    def calculate_summary_by_category(cls, db: Session) -> List[Dict[str, Any]]:
        """Calculate compliance summary grouped by category (for API response).
        
        This returns the format expected by the compliance-summary endpoint:
        [{category, total_obligations, average_coverage}, ...]
        
        Args:
            db: SQLAlchemy session
            
        Returns:
            List of category summaries with coverage scores
        """
        summary = []
        
        for category in ObligationCategory:
            category_info = cls.calculate_category_coverage(db, category)
            if category_info["total_obligations"] > 0:
                summary.append({
                    "category": category_info["category"],
                    "total_obligations": category_info["total_obligations"],
                    "average_coverage": category_info["average_coverage"],
                })
        
        return summary


def get_scorer() -> ComplianceCoverageScorer:
    """Get the compliance scorer instance (singleton pattern)."""
    return ComplianceCoverageScorer()
