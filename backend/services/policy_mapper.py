"""
Policy Mapping Service
Maps regulatory obligations to internal policies using AI
"""

import logging
import json
import re
from typing import Dict, Any, List

from config import Config
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class PolicyMapper:
    """
    Maps regulatory obligations to internal policy sections.
    
    Uses AI (Gemini) for semantic matching when available.
    Falls back to keyword-based matching.
    """
    
    def __init__(self):
        """Initialize the policy mapper."""
        self.use_ai = Config.is_configured()
        logger.info(f"PolicyMapper initialized - AI: {self.use_ai}")
    
    def map_obligation_to_policies(
        self,
        obligation_text: str,
        obligation_source: str,
        policy_texts: List[Dict[str, str]],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Map an obligation to relevant policy sections.
        
        Args:
            obligation_text: The regulatory obligation
            obligation_source: Where it came from
            policy_texts: List of dicts with 'name' and 'text'
            confidence_threshold: Minimum confidence for match
            
        Returns:
            Dict with mapped policies and confidence scores
        """
        try:
            # Try AI mapping first
            if self.use_ai and policy_texts:
                logger.info("Mapping with AI...")
                mappings = self._map_with_ai(obligation_text, policy_texts)
                if mappings:
                    return self._format_mapping_response(
                        obligation_text, mappings, confidence_threshold
                    )
                logger.warning("AI mapping failed, using keyword fallback...")
            
            # Fallback to keyword-based mapping
            mappings = self._map_with_keywords(obligation_text, policy_texts)
            return self._format_mapping_response(
                obligation_text, mappings, confidence_threshold
            )
        
        except Exception as e:
            logger.error(f"Policy mapping error: {str(e)}")
            raise
    
    def _map_with_ai(
        self,
        obligation_text: str,
        policy_texts: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Map obligation to policies using Gemini AI.
        """
        try:
            # Prepare policy summaries
            policies_str = "\n".join([
                f"POLICY [{p['name']}]:\n{p['text'][:1000]}"
                for p in policy_texts[:5]  # Limit to avoid token overflow
            ])
            
            prompt = f"""Analyze this regulatory obligation and find ALL relevant internal policies.

REGULATORY OBLIGATION:
{obligation_text[:1000]}

INTERNAL POLICIES:
{policies_str}

For EACH policy section that addresses or relates to this obligation, provide JSON:
{{
  "policy_name": "Policy name",
  "relevant_excerpts": ["Excerpt 1 showing relevance", "Excerpt 2"],
  "coverage_level": "fully_covered" | "partially_covered" | "not_covered",
  "confidence_score": 0.85,
  "mapping_reason": "Why this policy addresses the obligation"
}}

Return only a JSON array with findings. Be thorough - include partial matches.
Example format:
[{{"policy_name": "Security Policy", "relevant_excerpts": [...], "coverage_level": "partially_covered", "confidence_score": 0.75, "mapping_reason": "Addresses data access controls"}}]
"""
            
            response = GeminiService.generate_text(prompt, max_tokens=2000)
            logger.info("✓ AI mapping complete")
            
            # Parse response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                mappings = json.loads(json_match.group())
                return mappings if isinstance(mappings, list) else [mappings]
        
        except Exception as e:
            logger.warning(f"AI mapping failed: {str(e)}")
            return []
    
    def _map_with_keywords(
        self,
        obligation_text: str,
        policy_texts: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Map obligation using keyword-based matching (fallback).
        """
        mappings = []
        obligation_lower = obligation_text.lower()
        
        for policy in policy_texts:
            policy_text = policy.get('text', '').lower()
            policy_name = policy.get('name', 'Unknown Policy')
            
            # Extract key terms from obligation
            keywords = self._extract_keywords(obligation_text)
            
            # Count matches
            matches = sum(1 for kw in keywords if kw in policy_text)
            coverage_score = min(1.0, matches / max(len(keywords), 1))
            
            # Determine coverage level
            if coverage_score >= 0.7:
                coverage = "fully_covered"
                confidence = 0.85
            elif coverage_score >= 0.4:
                coverage = "partially_covered"
                confidence = 0.65
            else:
                continue  # Skip if very low match
            
            # Extract relevant excerpts
            excerpts = self._extract_excerpts(policy_text, keywords, 3)
            
            mapping = {
                "policy_name": policy_name,
                "relevant_excerpts": excerpts,
                "coverage_level": coverage,
                "confidence_score": confidence,
                "mapping_reason": f"Found {matches} relevant policy sections"
            }
            mappings.append(mapping)
        
        return mappings
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from obligation."""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'is', 'are', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'must', 'may', 'might', 'can', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'if', 'it', 'that', 'this', 'these',
            'those', 'what', 'which', 'who', 'when', 'where', 'why', 'how'
        }
        
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        return list(set(keywords))[:10]
    
    def _extract_excerpts(self, text: str, keywords: List[str], max_count: int) -> List[str]:
        """Extract relevant excerpts from policy text."""
        sentences = text.split('.')
        excerpts = []
        
        for sentence in sentences:
            if any(kw in sentence for kw in keywords):
                excerpt = sentence.strip()[:200]
                if excerpt and excerpt not in excerpts:
                    excerpts.append(excerpt)
                    if len(excerpts) >= max_count:
                        break
        
        return excerpts
    
    def _format_mapping_response(
        self,
        obligation_text: str,
        mappings: List[Dict[str, Any]],
        threshold: float
    ) -> Dict[str, Any]:
        """Format mapping response."""
        filtered_mappings = [
            m for m in mappings
            if m.get('confidence_score', 0) >= threshold
        ]
        
        return {
            "obligation_text": obligation_text,
            "total_policies_analyzed": len(mappings),
            "matching_policies": len(filtered_mappings),
            "mappings": filtered_mappings,
            "overall_coverage": self._calculate_coverage(filtered_mappings)
        }
    
    def _calculate_coverage(self, mappings: List[Dict[str, Any]]) -> str:
        """Calculate overall coverage level."""
        if not mappings:
            return "not_covered"
        
        levels = [m.get('coverage_level') for m in mappings]
        
        if 'fully_covered' in levels:
            return "fully_covered"
        elif 'partially_covered' in levels:
            return "partially_covered"
        else:
            return "not_covered"


# Singleton instance
_policy_mapper = None

def get_policy_mapper() -> PolicyMapper:
    """Get or create the policy mapper."""
    global _policy_mapper
    if _policy_mapper is None:
        _policy_mapper = PolicyMapper()
    return _policy_mapper
