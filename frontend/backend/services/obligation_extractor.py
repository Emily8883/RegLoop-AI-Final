"""
Production-Quality Obligation Extraction Engine for RegLoop AI

Rule-based regulatory obligation extraction without any paid APIs.
Focuses on sentence-level accuracy with noise filtering and intelligent categorization.
"""

import logging
import re
from typing import List, Dict, Set, Any
from dataclasses import dataclass, asdict

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# ============================================================================
# Core Obligation Keywords
# ============================================================================

# Primary obligation indicator keywords
OBLIGATION_KEYWORDS = {
    "must", "shall", "required", "requirement",
    "mandatory", "comply", "compliance", "ensure",
    "maintain", "monitor", "review", "record",
    "report", "responsible for"
}

# ============================================================================
# Category Classification Keywords
# ============================================================================

CATEGORY_KEYWORDS = {
    "operational": {
        "maintain", "monitor", "operate", "perform",
        "process", "procedure", "operation", "implement",
        "conduct", "execute", "manage", "system", "workflow"
    },
    "reporting": {
        "report", "record", "document", "submit",
        "file", "notify", "communicate", "inform",
        "disclose", "announce", "filing", "declaration"
    },
    "security": {
        "security", "password", "authentication", "authorization",
        "encrypt", "protect", "access", "confidential",
        "data protection", "security control", "secure"
    },
    "compliance": {
        "comply", "regulatory", "requirement", "regulation",
        "law", "legal", "mandate", "compliance",
        "regulatory requirement", "comply with"
    }
}

# ============================================================================
# Priority Assessment Keywords
# ============================================================================

PRIORITY_KEYWORDS = {
    "high": {"shall", "mandatory", "required", "must"},
    "medium": {"must", "ensure"},
    "low": {"monitor", "review", "record"}
}

# ============================================================================
# Responsible Team Inference
# ============================================================================

TEAM_KEYWORDS = {
    "Finance": {"financial", "accounting", "budget", "payment", "revenue", "expense"},
    "Compliance": {"compliance", "regulatory", "regulation", "legal", "requirement"},
    "Operations": {"process", "procedure", "operation", "maintain", "perform"},
    "HR": {"employee", "staff", "training", "personnel", "workforce"},
    "IT": {"system", "data", "security", "technology", "network", "digital"},
    "Management": {"board", "executive", "management", "oversight", "governance"}
}


# ============================================================================
# Obligation Data Structure
# ============================================================================

@dataclass
class Obligation:
    """Structured obligation with all required fields."""
    obligation_id: str
    obligation_text: str
    category: str
    priority: str
    responsible_team: str
    evidence_required: str


# ============================================================================
# Production-Quality Obligation Extractor
# ============================================================================

class ObligationExtractor:
    """Production-quality obligation extraction engine."""

    def __init__(self):
        """Initialize extractor state."""
        self.seen_obligations: Set[str] = set()
        logger.info("ObligationExtractor initialized")

    def extract_obligations(self, document_text: str) -> Dict[str, Any]:
        """
        Extract high-quality obligations from document text.
        
        Process:
        1. Clean and preprocess text
        2. Remove noise (headings, page numbers, tables, metadata)
        3. Split into clean sentences
        4. Detect obligation keywords
        5. Filter short/irrelevant sentences
        6. Remove duplicates
        7. Classify and assign priority
        
        Args:
            document_text: Raw text from PDF or document
            
        Returns:
            Dict with 'obligations' key containing list of obligation dicts
            
        Raises:
            ValueError: If document_text is empty or invalid
        """
        if not document_text or not isinstance(document_text, str):
            raise ValueError("Document text must be non-empty string")

        logger.info(f"Extracting obligations from {len(document_text)} characters")
        
        try:
            # Reset state
            self.seen_obligations = set()
            
            # Clean and preprocess
            cleaned_text = self._preprocess_text(document_text)
            logger.debug(f"After preprocessing: {len(cleaned_text)} characters")
            
            # Split into sentences and filter noise
            sentences = self._extract_clean_sentences(cleaned_text)
            logger.info(f"Found {len(sentences)} candidate sentences after noise filtering")
            
            # Extract and deduplicate obligations
            obligations = self._extract_from_sentences(sentences)
            logger.info(f"Extracted {len(obligations)} obligations")
            
            return {
                "obligations": [asdict(ob) for ob in obligations]
            }
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise ValueError(f"Extraction error: {str(e)}")

    def _preprocess_text(self, text: str) -> str:
        """
        Clean and normalize document text.
        
        - Remove extra whitespace
        - Remove common noise patterns
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers (common patterns)
        text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bp\.\s*\d+\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove common headers/footers
        text = re.sub(r'(Copyright|© |All Rights Reserved|Confidential)', '', text, flags=re.IGNORECASE)
        
        return text.strip()

    def _extract_clean_sentences(self, text: str) -> List[str]:
        """
        Extract clean sentences, filtering out noise.
        
        Returns only sentences that:
        - Are > 20 characters
        - Contain obligation keywords
        - Are not headings, metadata, or tables
        """
        # First, remove section numbers and headers at line boundaries
        # This regex removes patterns like "1. Introduction", "2.1 Security", etc.
        text = re.sub(r'(?m)^\d+(\.\d+)?\s+[A-Za-z\s]+$\n', '', text)
        
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        clean_sentences = []
        
        for sentence in sentences:
            # Basic cleanup
            sentence = sentence.strip()
            
            # Skip empty or too short
            if not sentence or len(sentence) < 20:
                continue
            
            # Skip if looks like heading (all caps, etc)
            if self._is_heading(sentence):
                continue
            
            # Skip if looks like metadata/table
            if self._is_metadata_or_table(sentence):
                continue
            
            # Skip section intro text without obligations
            if self._is_section_intro(sentence):
                continue
            
            # Must contain obligation keyword
            if not self._has_obligation_keyword(sentence):
                continue
            
            clean_sentences.append(sentence)
        
        return clean_sentences

    @staticmethod
    def _is_section_intro(sentence: str) -> bool:
        """Check if sentence is just an introductory section statement."""
        # Patterns like "This policy establishes", "The following describes", etc.
        intro_patterns = [
            r'^This\s+(policy|document|section)\s+(establishes|describes|outlines|defines)',
            r'^The\s+(following|below|next)\s+(section|requirement|item)',
            r'^Section\s+\d+',
            r'^\d+\.\s+\w+',  # "1. Introduction" style
        ]
        
        for pattern in intro_patterns:
            if re.match(pattern, sentence, re.IGNORECASE):
                # Make sure it actually has an obligation keyword
                return not any(kw in sentence.lower() for kw in [
                    "must", "shall", "required", "mandatory", 
                    "responsible for", "ensure", "maintain"
                ])
        
        return False

    @staticmethod
    def _is_heading(sentence: str) -> bool:
        """Check if sentence looks like a heading."""
        # All caps with few words
        if sentence.isupper() and len(sentence.split()) < 5:
            return True
        
        # Ends with colon (typical heading pattern)
        if sentence.rstrip().endswith(':') and len(sentence.split()) < 6:
            return True
        
        # Very short with specific patterns
        if len(sentence.split()) <= 3 and (
            sentence.endswith(':') or 
            sentence.isupper() or 
            sentence[0].isupper()
        ):
            return True
        
        return False

    @staticmethod
    def _is_metadata_or_table(sentence: str) -> bool:
        """Check if sentence is metadata, table content, or formatting."""
        # Too many numbers/special chars (likely table)
        special_count = sum(1 for c in sentence if c.isdigit() or c in '%$,|')
        if special_count > len(sentence) * 0.3:
            return True
        
        # Contains multiple pipes (table delimiter)
        if sentence.count('|') > 2:
            return True
        
        # Very long sequence of numbers
        if re.search(r'\d{10,}', sentence):
            return True
        
        # Looks like table header
        if sentence.count('\t') > 2 or sentence.count('  ') > 4:
            return True
        
        return False

    @staticmethod
    def _has_obligation_keyword(sentence: str) -> bool:
        """Check if sentence contains any obligation keyword."""
        sentence_lower = sentence.lower()
        return any(kw in sentence_lower for kw in OBLIGATION_KEYWORDS)

    def _extract_from_sentences(self, sentences: List[str]) -> List[Obligation]:
        """Convert sentences to Obligation objects."""
        obligations = []
        
        for idx, sentence in enumerate(sentences, 1):
            # Check for duplicate
            normalized = self._normalize_text(sentence)
            if self._is_duplicate(normalized):
                logger.debug(f"Skipping duplicate: {sentence[:50]}...")
                continue
            
            # Record this obligation
            self.seen_obligations.add(normalized)
            
            # Create obligation with 6 required fields
            obligation = Obligation(
                obligation_id=f"OBL_{len(obligations)+1:04d}",
                obligation_text=self._clean_sentence(sentence),
                category=self._classify_category(sentence),
                priority=self._determine_priority(sentence),
                responsible_team=self._infer_team(sentence),
                evidence_required=self._generate_evidence(sentence)
            )
            
            obligations.append(obligation)
            
            # Limit to reasonable number
            if len(obligations) >= 50:
                logger.warning("Reached 50 obligation limit")
                break
        
        return obligations

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for duplicate comparison."""
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _is_duplicate(self, normalized: str) -> bool:
        """Check if obligation is duplicate."""
        # Exact match
        if normalized in self.seen_obligations:
            return True
        
        # Similarity check (80% threshold)
        for seen in self.seen_obligations:
            if self._similarity(normalized, seen) > 0.80:
                return True
        
        return False

    @staticmethod
    def _similarity(text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0

    @staticmethod
    def _clean_sentence(sentence: str) -> str:
        """Clean and finalize sentence text."""
        # Remove extra whitespace
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        
        # Ensure proper capitalization
        if sentence and not sentence[0].isupper():
            sentence = sentence[0].upper() + sentence[1:]
        
        # Ensure ends with period if not already
        if sentence and sentence[-1] not in '.!?:':
            sentence += '.'
        
        return sentence

    @staticmethod
    def _classify_category(sentence: str) -> str:
        """Classify obligation into 4 categories."""
        sentence_lower = sentence.lower()
        
        # Check each category's keywords
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in sentence_lower for kw in keywords):
                return category
        
        # Default to compliance if no match
        return "compliance"

    @staticmethod
    def _determine_priority(sentence: str) -> str:
        """Assign priority level: high, medium, or low."""
        sentence_lower = sentence.lower()
        
        # High priority keywords
        if any(kw in sentence_lower for kw in PRIORITY_KEYWORDS["high"]):
            return "high"
        
        # Medium priority keywords
        if any(kw in sentence_lower for kw in PRIORITY_KEYWORDS["medium"]):
            return "medium"
        
        # Low priority keywords
        if any(kw in sentence_lower for kw in PRIORITY_KEYWORDS["low"]):
            return "low"
        
        # Default to medium
        return "medium"

    @staticmethod
    def _infer_team(sentence: str) -> str:
        """Infer responsible team."""
        sentence_lower = sentence.lower()
        
        # Match team keywords
        for team, keywords in TEAM_KEYWORDS.items():
            if any(kw in sentence_lower for kw in keywords):
                return team
        
        # Default to Compliance
        return "Compliance"

    @staticmethod
    def _generate_evidence(sentence: str) -> str:
        """Generate evidence requirements based on category and keywords."""
        sentence_lower = sentence.lower()
        
        # Reporting category
        if any(kw in sentence_lower for kw in ["report", "filing", "submit", "notify"]):
            return "Dated reports with submission evidence, filing receipts"
        
        # Documentation category
        if any(kw in sentence_lower for kw in ["document", "record", "maintain", "archive"]):
            return "Records with creation/modification dates, maintained archive"
        
        # Security category
        if any(kw in sentence_lower for kw in ["security", "authentication", "password", "encryption"]):
            return "Security policies, access logs, encryption certificates"
        
        # Operational category
        if any(kw in sentence_lower for kw in ["maintain", "monitor", "perform", "operate"]):
            return "Process logs, monitoring reports, operational records"
        
        # Default
        return "Supporting documentation and compliance records"


# ============================================================================
# Singleton Extractor
# ============================================================================

_extractor: ObligationExtractor = None


def get_extractor() -> ObligationExtractor:
    """Get or create global extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = ObligationExtractor()
        logger.info("Created new ObligationExtractor singleton")
    return _extractor
