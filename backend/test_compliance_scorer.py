"""Test suite for compliance coverage scoring."""

import sys
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, '.')

from database.db import get_db, SessionLocal, init_db
from database.models import Document, DocumentType, Obligation, PriorityLevel, ObligationCategory, GapAnalysis
from services.compliance_scorer import get_scorer


def setup_test_data(db: Session):
    """Create sample obligations for testing compliance scoring."""
    
    # Clear existing data
    db.query(GapAnalysis).delete()
    db.query(Obligation).delete()
    db.query(Document).delete()
    db.commit()
    
    # Create sample document
    doc = Document(
        filename="test_regulation.pdf",
        document_type=DocumentType.REGULATION,
        text_length=1000,
        raw_text="Sample regulation text for testing"
    )
    db.add(doc)
    db.flush()
    
    # Sample obligations with various priorities and categories
    test_obligations = [
        # Operational - High (90)
        ("OBL_0001", "The system shall support USB firmware upgrades.", ObligationCategory.OPERATIONAL, PriorityLevel.HIGH, "IT"),
        ("OBL_0002", "Organizations shall implement security controls.", ObligationCategory.OPERATIONAL, PriorityLevel.HIGH, "Compliance"),
        ("OBL_0003", "All data shall be encrypted at rest.", ObligationCategory.OPERATIONAL, PriorityLevel.HIGH, "IT"),
        
        # Reporting - High (90)
        ("OBL_0004", "Vendors shall report incidents within 24 hours.", ObligationCategory.REPORTING, PriorityLevel.HIGH, "Compliance"),
        ("OBL_0005", "Security events shall be logged and reported.", ObligationCategory.REPORTING, PriorityLevel.HIGH, "IT"),
        
        # Security - High (90)
        ("OBL_0006", "Authentication credentials must be encrypted.", ObligationCategory.SECURITY, PriorityLevel.HIGH, "IT"),
        ("OBL_0007", "Access controls shall be implemented.", ObligationCategory.SECURITY, PriorityLevel.HIGH, "IT"),
        
        # Compliance - High (90)
        ("OBL_0008", "Regulatory requirements shall be documented.", ObligationCategory.COMPLIANCE, PriorityLevel.HIGH, "Compliance"),
        
        # Operational - Medium (70)
        ("OBL_0009", "Systems must be monitored for performance.", ObligationCategory.OPERATIONAL, PriorityLevel.MEDIUM, "Operations"),
        ("OBL_0010", "Maintenance procedures must be documented.", ObligationCategory.OPERATIONAL, PriorityLevel.MEDIUM, "Operations"),
        
        # Reporting - Medium (70)
        ("OBL_0011", "Compliance status must be reported quarterly.", ObligationCategory.REPORTING, PriorityLevel.MEDIUM, "Compliance"),
        
        # Security - Medium (70)
        ("OBL_0012", "Passwords must meet complexity requirements.", ObligationCategory.SECURITY, PriorityLevel.MEDIUM, "IT"),
        
        # Operational - Low (50)
        ("OBL_0013", "Operations should monitor system health.", ObligationCategory.OPERATIONAL, PriorityLevel.LOW, "Operations"),
        ("OBL_0014", "Reviews should be conducted monthly.", ObligationCategory.OPERATIONAL, PriorityLevel.LOW, "Operations"),
        
        # Compliance - Low (50)
        ("OBL_0015", "Documentation should be retained for records.", ObligationCategory.COMPLIANCE, PriorityLevel.LOW, "Compliance"),
    ]
    
    for obl_id, text, category, priority, team in test_obligations:
        ob = Obligation(
            document_id=doc.id,
            obligation_id=obl_id,
            obligation_text=text,
            category=category,
            priority=priority,
            responsible_team=team,
            evidence_required="Process logs, documentation, audit reports"
        )
        db.add(ob)
        db.flush()
        
        # Create gap analysis record (can have coverage_score pre-calculated or use on-demand)
        gap = GapAnalysis(
            obligation_id=ob.id,
            status="open",
            coverage_score=0.0,  # Will be calculated on-demand
            gap_summary=f"Gap analysis for {obl_id}"
        )
        db.add(gap)
    
    db.commit()
    return doc


def test_individual_obligation_scoring():
    """Test scoring of individual obligations based on priority."""
    print("\n" + "="*80)
    print("TEST 1: Individual Obligation Scoring")
    print("="*80)
    
    scorer = get_scorer()
    
    # Test each priority level
    test_cases = [
        (PriorityLevel.HIGH, 90),
        (PriorityLevel.MEDIUM, 70),
        (PriorityLevel.LOW, 50),
    ]
    
    for priority, expected_score in test_cases:
        score = scorer.get_score_for_priority(priority)
        status = "✓" if score == expected_score else "✗"
        print(f"{status} {priority.value:10} → {score:3} points (expected {expected_score})")


def test_category_coverage():
    """Test average coverage calculation per category."""
    print("\n" + "="*80)
    print("TEST 2: Category Coverage Calculation")
    print("="*80)
    
    db = SessionLocal()
    setup_test_data(db)
    
    scorer = get_scorer()
    
    # Calculate coverage for each category
    categories = [
        ObligationCategory.OPERATIONAL,
        ObligationCategory.REPORTING,
        ObligationCategory.SECURITY,
        ObligationCategory.COMPLIANCE,
    ]
    
    for category in categories:
        result = scorer.calculate_category_coverage(db, category)
        if result["total_obligations"] > 0:
            print(f"\n{result['category'].upper()}:")
            print(f"  Total Obligations: {result['total_obligations']}")
            print(f"  Individual Scores: {result['scores']}")
            print(f"  Average Coverage: {result['average_coverage']}")
    
    db.close()


def test_overall_compliance():
    """Test overall compliance score calculation."""
    print("\n" + "="*80)
    print("TEST 3: Overall Compliance Score")
    print("="*80)
    
    db = SessionLocal()
    setup_test_data(db)
    
    scorer = get_scorer()
    
    # Calculate overall compliance
    compliance_report = scorer.calculate_overall_compliance(db)
    
    print(f"\nOverall Compliance Score: {compliance_report['overall_compliance_score']}")
    print(f"Total Obligations: {compliance_report['total_obligations']}")
    
    print("\nPer-Category Breakdown:")
    for category_info in compliance_report['categories']:
        print(f"  {category_info['category']:15} - {category_info['total_obligations']:2} obligations, avg coverage: {category_info['average_coverage']:6.1f}")
    
    print("\nPriority Level Breakdown:")
    priority_stats = compliance_report['priority_breakdown']
    print(f"  HIGH:   {priority_stats['high']:2} obligations, avg coverage: {priority_stats['high_coverage']:6.1f}")
    print(f"  MEDIUM: {priority_stats['medium']:2} obligations, avg coverage: {priority_stats['medium_coverage']:6.1f}")
    print(f"  LOW:    {priority_stats['low']:2} obligations, avg coverage: {priority_stats['low_coverage']:6.1f}")
    
    db.close()


def test_api_response_format():
    """Test that the response format matches API requirements."""
    print("\n" + "="*80)
    print("TEST 4: API Response Format Validation")
    print("="*80)
    
    db = SessionLocal()
    setup_test_data(db)
    
    scorer = get_scorer()
    compliance_report = scorer.calculate_overall_compliance(db)
    
    # Validate response structure
    required_keys = ["overall_compliance_score", "total_obligations", "categories", "priority_breakdown"]
    all_present = all(key in compliance_report for key in required_keys)
    
    print(f"\n{'✓' if all_present else '✗'} Response has all required fields: {all_present}")
    print(f"  Fields: {list(compliance_report.keys())}")
    
    # Validate categories structure
    if compliance_report['categories']:
        category = compliance_report['categories'][0]
        category_keys = ["category", "total_obligations", "average_coverage"]
        category_valid = all(key in category for key in category_keys)
        print(f"\n{'✓' if category_valid else '✗'} Category object has required fields: {category_valid}")
        print(f"  Fields: {list(category.keys())}")
        print(f"\n  Example Category Response:")
        print(f"    {category}")
    
    # Print full response
    print(f"\nFull API Response:")
    import json
    print(json.dumps(compliance_report, indent=2))
    
    db.close()


def test_empty_database():
    """Test behavior with empty database."""
    print("\n" + "="*80)
    print("TEST 5: Empty Database Handling")
    print("="*80)
    
    db = SessionLocal()
    
    # Clear database
    db.query(GapAnalysis).delete()
    db.query(Obligation).delete()
    db.query(Document).delete()
    db.commit()
    
    scorer = get_scorer()
    compliance_report = scorer.calculate_overall_compliance(db)
    
    print(f"\nOverall Compliance Score (empty): {compliance_report['overall_compliance_score']}")
    print(f"Total Obligations (empty): {compliance_report['total_obligations']}")
    print(f"Categories (empty): {compliance_report['categories']}")
    print(f"Priority Breakdown (empty): {compliance_report['priority_breakdown']}")
    
    expected_zero = compliance_report['overall_compliance_score'] == 0
    print(f"\n{'✓' if expected_zero else '✗'} Empty database returns 0 score: {expected_zero}")
    
    db.close()


def print_scoring_rules():
    """Print the scoring rules for reference."""
    print("\n" + "="*80)
    print("COMPLIANCE COVERAGE SCORING RULES (MVP)")
    print("="*80)
    print("""
Priority-Based Scoring:
  HIGH Priority:    90 points
  MEDIUM Priority:  70 points
  LOW Priority:     50 points

Calculation Method:
  1. Each obligation gets a score based on its priority level
  2. Category average = mean of all obligation scores in that category
  3. Overall score = mean of all obligation scores across all obligations

Example:
  If you have:
  - 5 HIGH priority obligations (5 × 90 = 450)
  - 3 MEDIUM priority obligations (3 × 70 = 210)
  - 2 LOW priority obligations (2 × 50 = 100)
  
  Overall score = (450 + 210 + 100) / 10 = 76.0
    """)


def main():
    """Run all compliance scoring tests."""
    print("\n" + "="*80)
    print("COMPLIANCE COVERAGE SCORING TEST SUITE")
    print("="*80)
    
    init_db()
    
    try:
        print_scoring_rules()
        test_individual_obligation_scoring()
        test_category_coverage()
        test_overall_compliance()
        test_api_response_format()
        test_empty_database()
        
        print("\n" + "="*80)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
