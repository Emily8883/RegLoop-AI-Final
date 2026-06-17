"""
Policy Pull Request Generator Service
Generates policy amendment recommendations based on compliance gaps
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass

from config import Config
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


@dataclass
class PolicyAmendment:
    """Structured policy amendment proposal"""
    gap_description: str
    original_policy_text: str
    proposed_amendment: str
    regulatory_citation: str
    suggested_owner: str
    risk_level: str  # high, medium, low
    confidence_score: float
    before_text: str
    after_text: str
    diff_summary: str


class PolicyPRGenerator:
    """
    Generates Policy Pull Requests (amendments) based on identified compliance gaps.
    
    Uses AI (Gemini) when available for better amendments, falls back to templates.
    """
    
    def __init__(self):
        """Initialize the PR generator."""
        self.use_ai = Config.is_configured()
        logger.info(f"PolicyPRGenerator initialized - AI: {self.use_ai}")
    
    def generate_pr_for_gap(
        self,
        gap_description: str,
        obligation_text: str,
        regulatory_citation: str,
        current_policy_text: str,
        priority: str,
        category: str,
        responsible_team: str
    ) -> Dict[str, Any]:
        """
        Generate a policy amendment for a compliance gap.
        
        Args:
            gap_description: Why there's a gap
            obligation_text: The regulatory obligation
            regulatory_citation: Source reference
            current_policy_text: Current policy section
            priority: high, medium, low
            category: operational, reporting, security, compliance
            responsible_team: Who should own this
            
        Returns:
            Dict with PR details and amendment proposal
        """
        try:
            # Try AI generation first
            if self.use_ai:
                logger.info("Generating PR with AI...")
                amendment = self._generate_with_gemini(
                    gap_description, obligation_text, regulatory_citation,
                    current_policy_text, priority, category, responsible_team
                )
                if amendment:
                    return self._format_pr_response(amendment)
                logger.warning("AI generation failed, using fallback...")
            
            # Fallback: template-based generation
            amendment = self._generate_with_template(
                gap_description, obligation_text, regulatory_citation,
                current_policy_text, priority, category, responsible_team
            )
            return self._format_pr_response(amendment)
        
        except Exception as e:
            logger.error(f"PR generation error: {str(e)}")
            raise
    
    def _generate_with_gemini(
        self,
        gap_description: str,
        obligation_text: str,
        regulatory_citation: str,
        current_policy_text: str,
        priority: str,
        category: str,
        responsible_team: str
    ) -> PolicyAmendment:
        """
        Generate amendment using Gemini AI.
        """
        try:
            prompt = f"""Generate a policy amendment to address a compliance gap.

GAP DESCRIPTION:
{gap_description}

REGULATORY OBLIGATION:
{obligation_text}

REGULATORY CITATION:
{regulatory_citation}

CURRENT POLICY (if any):
{current_policy_text or "No existing policy"}

PRIORITY: {priority}
CATEGORY: {category}
RESPONSIBLE TEAM: {responsible_team}

Provide a JSON response with:
{{
  "proposed_amendment": "Complete revised policy text that addresses the obligation",
  "before_text": "Original policy section",
  "after_text": "New policy section",
  "diff_summary": "Summary of changes (2-3 sentences)",
  "suggested_owner": "Team that should implement",
  "confidence_score": 0.85
}}

Make the amendment:
1. Specific and actionable
2. Complete policy language (not just a note)
3. Clear about responsibilities
4. Include measurable outcomes where possible
5. Reference the regulation
"""
            
            response = GeminiService.generate_text(prompt, max_tokens=2000)
            logger.info("✓ Generated amendment with Gemini")
            
            # Parse response (simplified)
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return PolicyAmendment(
                    gap_description=gap_description,
                    original_policy_text=current_policy_text or "No existing policy",
                    proposed_amendment=data.get("proposed_amendment", ""),
                    regulatory_citation=regulatory_citation,
                    suggested_owner=data.get("suggested_owner", responsible_team),
                    risk_level=priority,
                    confidence_score=float(data.get("confidence_score", 0.85)),
                    before_text=data.get("before_text", "No existing policy"),
                    after_text=data.get("after_text", data.get("proposed_amendment", "")),
                    diff_summary=data.get("diff_summary", "Policy updated to address obligation")
                )
        except Exception as e:
            logger.warning(f"Gemini generation failed: {str(e)}")
            return None
    
    def _generate_with_template(
        self,
        gap_description: str,
        obligation_text: str,
        regulatory_citation: str,
        current_policy_text: str,
        priority: str,
        category: str,
        responsible_team: str
    ) -> PolicyAmendment:
        """
        Generate amendment using template-based approach (fallback).
        """
        # Create structured amendment from obligation
        amendment_text = f"""POLICY AMENDMENT: {category.upper()}

EFFECTIVE DATE: Upon approval

PURPOSE:
{obligation_text}

REGULATORY REQUIREMENT:
{regulatory_citation}

POLICY STATEMENT:
{responsible_team} is responsible for ensuring the following:

1. Regular Implementation: This obligation must be met in accordance with regulatory requirements.
2. Documentation: All actions taken to comply with this obligation must be documented.
3. Review: This policy must be reviewed {self._get_frequency(obligation_text)} to ensure ongoing compliance.
4. Responsibility: {responsible_team} shall be responsible for implementation and oversight.

COMPLIANCE PROCEDURES:
- Monitor and track compliance with this obligation
- Maintain documentation of compliance efforts
- Report status quarterly to compliance committee
- Escalate any compliance issues immediately

EVIDENCE OF COMPLIANCE:
- Complete documentation of all compliance activities
- Records demonstrating implementation
- Audit trail showing monitoring and review
"""
        
        return PolicyAmendment(
            gap_description=gap_description,
            original_policy_text=current_policy_text or "No existing policy",
            proposed_amendment=amendment_text,
            regulatory_citation=regulatory_citation,
            suggested_owner=responsible_team,
            risk_level=priority,
            confidence_score=0.70,  # Lower confidence for template-based
            before_text=current_policy_text or "No existing policy",
            after_text=amendment_text,
            diff_summary=f"Added policy section to address {category} obligation"
        )
    
    def _get_frequency(self, obligation_text: str) -> str:
        """Extract frequency from obligation text."""
        frequencies = {
            "daily": "daily",
            "weekly": "weekly",
            "monthly": "monthly",
            "quarterly": "quarterly",
            "annually": "annually",
            "yearly": "annually"
        }
        text_lower = obligation_text.lower()
        for key, value in frequencies.items():
            if key in text_lower:
                return value
        return "quarterly"
    
    def _format_pr_response(self, amendment: PolicyAmendment) -> Dict[str, Any]:
        """Format amendment as PR response."""
        return {
            "gap_description": amendment.gap_description,
            "original_policy_text": amendment.original_policy_text,
            "proposed_amendment": amendment.proposed_amendment,
            "regulatory_citation": amendment.regulatory_citation,
            "suggested_owner": amendment.suggested_owner,
            "risk_level": amendment.risk_level,
            "confidence_score": amendment.confidence_score,
            "before_text": amendment.before_text,
            "after_text": amendment.after_text,
            "diff_summary": amendment.diff_summary
        }


# Singleton instance
_pr_generator = None

def get_pr_generator() -> PolicyPRGenerator:
    """Get or create the PR generator."""
    global _pr_generator
    if _pr_generator is None:
        _pr_generator = PolicyPRGenerator()
    return _pr_generator
