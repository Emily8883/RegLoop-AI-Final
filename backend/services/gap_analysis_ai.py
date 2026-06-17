"""
AI-Powered Gap Analysis Service
Analyzes compliance gaps using Gemini AI with risk scoring
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from config import Config
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class GapAnalysisAI:
    """
    AI-powered gap analysis service.
    Provides intelligent gap analysis with risk scoring and recommendations.
    """
    
    def __init__(self):
        """Initialize gap analysis service."""
        self.use_ai = Config.is_configured()
        logger.info(f"GapAnalysisAI initialized - AI: {self.use_ai}")
    
    def analyze_gap_with_ai(
        self,
        obligation_text: str,
        obligation_category: str,
        obligation_priority: str,
        current_coverage: float,
        responsible_team: str,
        evidence_required: str
    ) -> Dict[str, Any]:
        """
        Perform AI-powered gap analysis.
        
        Args:
            obligation_text: The regulatory obligation
            obligation_category: Category (operational, security, etc.)
            obligation_priority: Priority (high, medium, low)
            current_coverage: Current coverage score (0-1)
            responsible_team: Team responsible
            evidence_required: What evidence is needed
            
        Returns:
            Dict with gap analysis, risk score, and recommendations
        """
        try:
            # Calculate risk score
            risk_score = self._calculate_risk_score(
                obligation_priority,
                current_coverage,
                obligation_category
            )
            
            # Determine gap severity
            gap_severity = self._determine_severity(risk_score, current_coverage)
            
            # Get AI recommendations if available
            recommendations = []
            if self.use_ai:
                recommendations = self._get_ai_recommendations(
                    obligation_text,
                    obligation_category,
                    gap_severity,
                    current_coverage,
                    responsible_team
                )
            
            if not recommendations:
                recommendations = self._get_template_recommendations(
                    obligation_category,
                    gap_severity,
                    responsible_team
                )
            
            # Build response
            return {
                "gap_analysis": {
                    "severity": gap_severity,
                    "risk_score": risk_score,
                    "coverage_gap": 1.0 - current_coverage,
                    "current_coverage": current_coverage,
                    "priority": obligation_priority,
                    "category": obligation_category,
                    "identified_at": datetime.utcnow().isoformat()
                },
                "recommendations": recommendations,
                "timeline": self._get_timeline(gap_severity),
                "responsible_team": responsible_team,
                "evidence_needed": evidence_required,
                "next_steps": self._get_next_steps(gap_severity)
            }
        
        except Exception as e:
            logger.error(f"Gap analysis error: {str(e)}")
            raise
    
    def _calculate_risk_score(
        self,
        priority: str,
        coverage: float,
        category: str
    ) -> float:
        """
        Calculate risk score (0-1, where 1 is highest risk).
        
        Formula: (priority_weight × (1 - coverage)) + category_weight
        """
        # Priority weights
        priority_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        
        # Category risk weights
        category_weights = {
            "security": 0.3,
            "compliance": 0.25,
            "reporting": 0.2,
            "operational": 0.15,
            "documentation": 0.1,
            "financial": 0.25,
            "training": 0.1,
            "other": 0.1
        }
        
        priority_weight = priority_weights.get(priority, 0.5)
        category_weight = category_weights.get(category, 0.1)
        
        # Risk = (priority impact × coverage gap) + category inherent risk
        risk = (priority_weight * (1.0 - coverage)) + (category_weight * 0.3)
        
        return min(1.0, max(0.0, risk))
    
    def _determine_severity(self, risk_score: float, coverage: float) -> str:
        """Determine gap severity based on risk score and coverage."""
        if risk_score >= 0.8 and coverage < 0.2:
            return "critical"
        elif risk_score >= 0.6 and coverage < 0.4:
            return "high"
        elif risk_score >= 0.4 and coverage < 0.7:
            return "medium"
        else:
            return "low"
    
    def _get_ai_recommendations(
        self,
        obligation_text: str,
        category: str,
        severity: str,
        coverage: float,
        team: str
    ) -> List[Dict[str, Any]]:
        """Get AI-powered recommendations using Gemini."""
        try:
            prompt = f"""Provide specific, actionable recommendations to close this compliance gap.

OBLIGATION:
{obligation_text}

CATEGORY: {category}
SEVERITY: {severity}
CURRENT COVERAGE: {coverage:.0%}
RESPONSIBLE TEAM: {team}

For this gap, provide 3-4 specific recommendations in JSON format:
[
  {{
    "action": "Specific action to take",
    "priority": "immediate|short-term|medium-term",
    "effort": "low|medium|high",
    "owner": "Team responsible",
    "success_criteria": "How to measure completion"
  }}
]

Return only valid JSON array."""

            response = GeminiService.generate_text(prompt, max_tokens=1000)
            logger.info("✓ Generated AI recommendations")
            
            # Parse recommendations
            import json
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                recs = json.loads(json_match.group())
                return recs if isinstance(recs, list) else []
        
        except Exception as e:
            logger.warning(f"AI recommendations failed: {str(e)}")
            return []
    
    def _get_template_recommendations(
        self,
        category: str,
        severity: str,
        team: str
    ) -> List[Dict[str, Any]]:
        """Get template-based recommendations (fallback)."""
        recommendations_map = {
            "security": [
                {
                    "action": "Conduct security assessment to identify protection gaps",
                    "priority": "immediate" if severity == "critical" else "short-term",
                    "effort": "medium",
                    "owner": team,
                    "success_criteria": "Assessment report completed with findings"
                },
                {
                    "action": "Implement security controls identified in assessment",
                    "priority": "short-term",
                    "effort": "high",
                    "owner": team,
                    "success_criteria": "All critical controls deployed and tested"
                },
                {
                    "action": "Document security procedures and train staff",
                    "priority": "medium-term",
                    "effort": "medium",
                    "owner": team,
                    "success_criteria": "100% staff completion of security training"
                }
            ],
            "compliance": [
                {
                    "action": "Map obligation to existing policies",
                    "priority": "immediate",
                    "effort": "low",
                    "owner": "Compliance",
                    "success_criteria": "Policy mapping completed"
                },
                {
                    "action": "Update policies to address obligation",
                    "priority": "short-term",
                    "effort": "medium",
                    "owner": "Compliance",
                    "success_criteria": "Policies updated and approved"
                },
                {
                    "action": "Implement monitoring and attestation",
                    "priority": "medium-term",
                    "effort": "medium",
                    "owner": "Compliance",
                    "success_criteria": "Monitoring plan in place with monthly reports"
                }
            ],
            "reporting": [
                {
                    "action": "Design reporting process and template",
                    "priority": "immediate",
                    "effort": "low",
                    "owner": team,
                    "success_criteria": "Report template approved"
                },
                {
                    "action": "Implement reporting system/tool",
                    "priority": "short-term",
                    "effort": "medium",
                    "owner": team,
                    "success_criteria": "System tested and operational"
                },
                {
                    "action": "Train staff on reporting procedures",
                    "priority": "medium-term",
                    "effort": "low",
                    "owner": team,
                    "success_criteria": "First report submitted on schedule"
                }
            ],
            "operational": [
                {
                    "action": "Document current operational procedures",
                    "priority": "immediate",
                    "effort": "low",
                    "owner": team,
                    "success_criteria": "Procedures documented"
                },
                {
                    "action": "Identify required improvements",
                    "priority": "short-term",
                    "effort": "medium",
                    "owner": team,
                    "success_criteria": "Gap analysis completed"
                },
                {
                    "action": "Implement and test improvements",
                    "priority": "medium-term",
                    "effort": "high",
                    "owner": team,
                    "success_criteria": "All improvements tested and operational"
                }
            ]
        }
        
        # Get recommendations for category or default to operational
        return recommendations_map.get(category, recommendations_map["operational"])
    
    def _get_timeline(self, severity: str) -> Dict[str, str]:
        """Get recommended timeline for gap closure."""
        timelines = {
            "critical": {
                "assessment": "Within 1 week",
                "remediation_start": "Within 2 weeks",
                "completion": "Within 30 days"
            },
            "high": {
                "assessment": "Within 2 weeks",
                "remediation_start": "Within 1 month",
                "completion": "Within 90 days"
            },
            "medium": {
                "assessment": "Within 1 month",
                "remediation_start": "Within 6 weeks",
                "completion": "Within 6 months"
            },
            "low": {
                "assessment": "Within 6 weeks",
                "remediation_start": "Within 3 months",
                "completion": "Within 12 months"
            }
        }
        
        return timelines.get(severity, timelines["medium"])
    
    def _get_next_steps(self, severity: str) -> List[str]:
        """Get immediate next steps."""
        if severity == "critical":
            return [
                "1. Schedule emergency meeting with stakeholders",
                "2. Assign incident commander",
                "3. Begin assessment within 24 hours",
                "4. Daily status updates",
                "5. Escalate to executive leadership"
            ]
        elif severity == "high":
            return [
                "1. Schedule kickoff meeting with team",
                "2. Create remediation project",
                "3. Begin assessment this week",
                "4. Weekly status updates",
                "5. Report to compliance committee"
            ]
        elif severity == "medium":
            return [
                "1. Create remediation plan",
                "2. Assign owner and timeline",
                "3. Begin assessment within 2 weeks",
                "4. Monthly status updates",
                "5. Monitor progress"
            ]
        else:
            return [
                "1. Add to backlog",
                "2. Monitor during reviews",
                "3. Assess feasibility",
                "4. Schedule when resources available"
            ]


# Singleton instance
_gap_analysis_ai = None

def get_gap_analysis_ai() -> GapAnalysisAI:
    """Get or create the gap analysis service."""
    global _gap_analysis_ai
    if _gap_analysis_ai is None:
        _gap_analysis_ai = GapAnalysisAI()
    return _gap_analysis_ai
