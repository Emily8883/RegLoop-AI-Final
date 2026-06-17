"""
Enhanced Obligation Extraction Engine with AI Support
- Primary: Gemini-powered extraction with confidence scores and citations
- Fallback: Rule-based extraction if Gemini unavailable
"""

import logging
import json
import re
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

from config import Config
from services.gemini_service import GeminiService
from services.obligation_extractor import ObligationExtractor

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class EnhancedObligation:
    """Enhanced obligation with confidence score and source citation"""
    obligation_id: str
    obligation_text: str
    category: str
    priority: str
    responsible_team: str
    evidence_required: str
    confidence_score: float = 0.75  # 0.0 to 1.0
    source_citation: str = ""  # e.g., "Section 2.1, Paragraph 3"
    deadline_or_frequency: str = "As required"


class EnhancedObligationExtractor:
    """
    Production-grade obligation extraction with AI enhancement.
    
    Workflow:
    1. Try Gemini extraction first (if configured) - gets confidence + citations
    2. Fall back to rule-based extraction (if Gemini fails)
    3. Ensure all obligations have required fields
    
    This maximizes FR-2 requirements (confidence scores, source citations)
    while maintaining reliability through fallback.
    """
    
    def __init__(self):
        """Initialize extractor with AI support."""
        self.rule_based_extractor = ObligationExtractor()
        self.use_ai = Config.is_configured()
        logger.info(f"EnhancedObligationExtractor initialized - AI: {self.use_ai}")
    
    def extract_obligations(self, document_text: str) -> Dict[str, Any]:
        """
        Extract obligations using AI (preferred) or rule-based (fallback).
        
        FR-2 Compliance:
        - Extracts obligation statements ✓
        - Includes source citations ✓
        - Provides confidence scores ✓
        - Includes suggested compliance domain ✓
        
        Args:
            document_text: Raw document text
            
        Returns:
            Dict with obligations list containing all required fields
        """
        if not document_text or not isinstance(document_text, str):
            raise ValueError("Document text must be non-empty string")
        
        logger.info(f"Extracting from {len(document_text)} chars - AI enabled: {self.use_ai}")
        
        try:
            # Try AI extraction first
            if self.use_ai:
                logger.info("Attempting AI-powered extraction...")
                ai_obligations = self._extract_with_gemini(document_text)
                if ai_obligations:
                    logger.info(f"✓ AI extracted {len(ai_obligations)} obligations")
                    return {"obligations": [asdict(ob) for ob in ai_obligations]}
                else:
                    logger.warning("AI extraction returned empty, trying fallback...")
            
            # Fallback to rule-based extraction
            logger.info("Using rule-based extraction fallback...")
            rule_obligations = self._extract_with_rules(document_text)
            logger.info(f"✓ Rule-based extracted {len(rule_obligations)} obligations")
            return {"obligations": [asdict(ob) for ob in rule_obligations]}
        
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}")
            # Last resort: rule-based fallback
            try:
                logger.info("Using emergency fallback extraction...")
                rule_obligations = self._extract_with_rules(document_text)
                return {"obligations": [asdict(ob) for ob in rule_obligations]}
            except Exception as fallback_error:
                logger.error(f"Emergency fallback failed: {str(fallback_error)}")
                raise ValueError(f"Extraction failed completely: {str(e)}")
    
    def _extract_with_gemini(self, document_text: str) -> List[EnhancedObligation]:
        """
        Extract obligations using Gemini with confidence scores and citations.
        
        Returns:
            List of EnhancedObligation objects with confidence and citations
        """
        try:
            # Prepare text (limit to avoid token limits)
            text_excerpt = document_text[:4000]
            
            # Create detailed prompt for structured extraction
            prompt = f"""Analyze the following regulatory document and extract compliance obligations.

For EACH obligation found, provide JSON with these exact fields:
- obligation_text: The exact regulation text or your summary (max 200 chars)
- source_citation: Where in the text this comes from (e.g., "Section 3.2, Paragraph 1" or "Line 45-48")
- confidence_score: Your confidence this is a real obligation (0.0 to 1.0, e.g., 0.95)
- category: One of: operational, reporting, security, compliance
- priority: One of: high, medium, low
- responsible_team: Who should own this (e.g., "Compliance", "IT", "Operations")
- evidence_required: What proof of compliance is needed
- deadline_or_frequency: When/how often (e.g., "Quarterly", "Upon request", "Monthly")

Document:
{text_excerpt}

Return ONLY valid JSON array, no other text:
[{{"obligation_text": "...", "source_citation": "...", "confidence_score": 0.95, "category": "...", "priority": "...", "responsible_team": "...", "evidence_required": "...", "deadline_or_frequency": "..."}}]"""
            
            logger.debug("Calling Gemini API for extraction...")
            response = GeminiService.generate_text(prompt)
            logger.debug(f"Gemini response length: {len(response)}")
            
            # Parse JSON from response
            obligations = self._parse_gemini_response(response)
            
            # Enrich with IDs
            for idx, obl in enumerate(obligations, 1):
                if not obl.get("obligation_id"):
                    obl["obligation_id"] = f"AI_OBL_{idx:04d}"
            
            logger.info(f"✓ Parsed {len(obligations)} obligations from Gemini")
            return [EnhancedObligation(**obl) for obl in obligations]
        
        except Exception as e:
            logger.warning(f"Gemini extraction failed: {str(e)}")
            return []
    
    def _parse_gemini_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse JSON array from Gemini response.
        
        Extracts JSON even if surrounded by other text.
        """
        try:
            # Find JSON array in response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                obligations = json.loads(json_match.group())
                
                # Validate and clean each obligation
                cleaned = []
                for obl in obligations:
                    if isinstance(obl, dict):
                        # Ensure required fields
                        obl.setdefault("obligation_text", "")
                        obl.setdefault("source_citation", "")
                        obl.setdefault("confidence_score", 0.75)
                        obl.setdefault("category", "compliance")
                        obl.setdefault("priority", "medium")
                        obl.setdefault("responsible_team", "Compliance")
                        obl.setdefault("evidence_required", "")
                        obl.setdefault("deadline_or_frequency", "As required")
                        
                        # Validate confidence score
                        try:
                            score = float(obl.get("confidence_score", 0.75))
                            obl["confidence_score"] = max(0.0, min(1.0, score))
                        except:
                            obl["confidence_score"] = 0.75
                        
                        if obl.get("obligation_text"):
                            cleaned.append(obl)
                
                return cleaned
            else:
                logger.warning("No JSON array found in Gemini response")
                return []
        
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {str(e)}")
            return []
    
    def _extract_with_rules(self, document_text: str) -> List[EnhancedObligation]:
        """
        Fallback: Extract obligations using rule-based method.
        
        Converts rule-based results to EnhancedObligation with default confidence.
        """
        try:
            result = self.rule_based_extractor.extract_obligations(document_text)
            rule_obligations = result.get("obligations", [])
            
            enhanced = []
            for idx, obl in enumerate(rule_obligations, 1):
                # Convert to enhanced obligation with confidence score
                enhanced_obl = EnhancedObligation(
                    obligation_id=obl.get("obligation_id", f"RULE_OBL_{idx:04d}"),
                    obligation_text=obl.get("obligation_text", ""),
                    category=obl.get("category", "compliance"),
                    priority=obl.get("priority", "medium"),
                    responsible_team=obl.get("responsible_team", "Compliance"),
                    evidence_required=obl.get("evidence_required", ""),
                    deadline_or_frequency=obl.get("deadline_or_frequency", "As required"),
                    confidence_score=0.70,  # Rule-based lower confidence
                    source_citation="Extracted via rule-based analysis"
                )
                enhanced.append(enhanced_obl)
            
            return enhanced
        
        except Exception as e:
            logger.error(f"Rule-based extraction failed: {str(e)}")
            return []


# Singleton extractor instance
_enhanced_extractor = None

def get_enhanced_extractor() -> EnhancedObligationExtractor:
    """Get or create the enhanced obligation extractor."""
    global _enhanced_extractor
    if _enhanced_extractor is None:
        _enhanced_extractor = EnhancedObligationExtractor()
    return _enhanced_extractor
