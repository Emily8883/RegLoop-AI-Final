"""
Testing and Examples for RegLoop AI Obligation Extraction Engine

Complete examples demonstrating:
1. Direct service usage
2. Database integration
3. FastAPI endpoint workflows
4. Testing scenarios
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.obligation_extractor import ObligationExtractor, get_extractor
from database.db import SessionLocal, init_db
from database.models import Document, Obligation, GapAnalysis, DocumentType, ObligationCategory
import json


# ============================================================================
# Test 1: Direct Service Usage
# ============================================================================

def test_direct_extraction():
    """Test obligation extraction without database."""
    print("\n" + "="*70)
    print("TEST 1: Direct Service Usage")
    print("="*70)

    # Sample regulatory document
    sample_text = """
    REGULATORY COMPLIANCE REQUIREMENTS
    
    All organizations must implement and maintain a comprehensive cybersecurity 
    program. The program shall include documented security policies and procedures 
    that address access controls, data protection, and incident response.
    
    Organizations are required to conduct annual security awareness training for 
    all employees. This training requirement ensures staff compliance with security 
    policies.
    
    Financial institutions shall maintain audit logs for at least 7 years. 
    These records must be archived in a secure location and reviewed quarterly 
    for suspicious activities.
    
    The compliance team is responsible for monitoring regulatory changes and 
    communicating updates to relevant departments. Management must approve 
    all policy changes within 30 days of submission.
    
    All documentation regarding compliance activities must be preserved 
    and made available for regulatory inspection. Evidence of compliance 
    should include training records, audit reports, and policy acknowledgments.
    """

    try:
        extractor = get_extractor()
        result = extractor.extract_obligations(sample_text)
        obligations = result.get("obligations", [])

        print(f"\n✓ Successfully extracted {len(obligations)} obligations\n")

        for ob in obligations[:3]:  # Show first 3
            print(f"ID: {ob['obligation_id']}")
            print(f"Text: {ob['obligation_text']}")
            print(f"Category: {ob['category']}")
            print(f"Priority: {ob['priority']}")
            print(f"Team: {ob['responsible_team']}")
            print(f"Deadline: {ob['deadline_or_frequency']}")
            print("-" * 70)

    except Exception as e:
        print(f"✗ Error: {str(e)}")


# ============================================================================
# Test 2: Database Integration
# ============================================================================

def test_database_integration():
    """Test obligation storage in database."""
    print("\n" + "="*70)
    print("TEST 2: Database Integration")
    print("="*70)

    try:
        # Initialize database
        init_db()
        db = SessionLocal()

        # Create test document
        doc = Document(
            filename="test_regulation.pdf",
            document_type=DocumentType.REGULATION,
            text_length=500,
            raw_text="""
            All companies must maintain detailed records of financial transactions.
            The finance team shall document all payments and receipts with proper 
            authorization. Monthly financial statements are required for board review.
            """
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        print(f"\n✓ Created test document with ID: {doc.id}")

        # Extract and save obligations
        extractor = get_extractor()
        result = extractor.extract_obligations(doc.raw_text)
        obligations = result.get("obligations", [])

        created = 0
        for ob_dict in obligations:
            ob = Obligation(
                document_id=doc.id,
                obligation_id=ob_dict["obligation_id"],
                obligation_text=ob_dict["obligation_text"],
                category=ob_dict["category"],
                priority=ob_dict["priority"],
                responsible_team=ob_dict["responsible_team"],
                evidence_required=ob_dict["evidence_required"],
                deadline_or_frequency=ob_dict["deadline_or_frequency"],
                risk_if_not_met=ob_dict["risk_if_not_met"]
            )
            db.add(ob)
            created += 1

        db.commit()
        print(f"✓ Saved {created} obligations to database")

        # Query back
        saved_obs = db.query(Obligation).filter(Obligation.document_id == doc.id).all()
        print(f"✓ Retrieved {len(saved_obs)} obligations from database")

        for ob in saved_obs[:2]:
            print(f"\n  ID: {ob.obligation_id}")
            print(f"  Text: {ob.obligation_text[:50]}...")
            print(f"  Category: {ob.category} | Priority: {ob.priority}")

        db.close()

    except Exception as e:
        print(f"✗ Error: {str(e)}")


# ============================================================================
# Test 3: Category Classification
# ============================================================================

def test_category_classification():
    """Test category detection accuracy."""
    print("\n" + "="*70)
    print("TEST 3: Category Classification")
    print("="*70)

    test_cases = [
        ("Maintain financial records and audit trails", "financial"),
        ("Document all operational procedures and workflows", "documentation"),
        ("Submit quarterly reports to regulatory authority", "reporting"),
        ("Provide employee training on compliance policies", "training"),
        ("Conduct annual audit of security controls", "compliance"),
    ]

    extractor = ObligationExtractor()
    correct = 0

    for text, expected_category in test_cases:
        detected = extractor._classify_category(text)
        status = "✓" if detected == expected_category else "✗"
        correct += (detected == expected_category)

        print(f"{status} '{text}'")
        print(f"  Expected: {expected_category}, Got: {detected}\n")

    print(f"Accuracy: {correct}/{len(test_cases)} ({100*correct/len(test_cases):.0f}%)")


# ============================================================================
# Test 4: Priority Assessment
# ============================================================================

def test_priority_assessment():
    """Test priority level detection."""
    print("\n" + "="*70)
    print("TEST 4: Priority Assessment")
    print("="*70)

    test_cases = [
        ("Organizations must implement critical security controls immediately", "critical"),
        ("We recommend implementing best practices for data governance", "medium"),
        ("Financial reporting should follow GAAP standards", "high"),
    ]

    extractor = ObligationExtractor()

    for text, expected_priority in test_cases:
        detected = extractor._determine_priority(text)
        status = "✓" if detected == expected_priority else "✗"

        print(f"{status} '{text}'")
        print(f"  Priority: {detected}\n")


# ============================================================================
# Test 5: Duplicate Detection
# ============================================================================

def test_duplicate_detection():
    """Test duplicate removal."""
    print("\n" + "="*70)
    print("TEST 5: Duplicate Detection")
    print("="*70)

    sentences = [
        "Organizations must maintain security records.",
        "Organizations must maintain security records.",  # Exact duplicate
        "Organizations must maintain security records for audit purposes.",  # Similar
        "The finance team shall document all transactions.",  # Different
    ]

    extractor = ObligationExtractor()
    result = extractor.extract_obligations(" ".join(sentences))
    obligations = result.get("obligations", [])

    print(f"\nInput: {len(sentences)} sentences")
    print(f"Output: {len(obligations)} unique obligations")
    print(f"Duplicates removed: {len(sentences) - len(obligations)}")

    for ob in obligations:
        print(f"  - {ob['obligation_text'][:60]}...")


# ============================================================================
# Test 6: Full Workflow Simulation
# ============================================================================

def test_full_workflow():
    """Simulate complete analysis workflow."""
    print("\n" + "="*70)
    print("TEST 6: Full Workflow Simulation")
    print("="*70)

    comprehensive_text = """
    DATA PROTECTION AND PRIVACY REGULATION
    
    1. GENERAL REQUIREMENTS
    Organizations shall implement a comprehensive data protection program.
    The program must include written policies, procedures, and controls.
    
    2. DATA CLASSIFICATION
    All data shall be classified according to sensitivity levels.
    Classification must be documented and reviewed annually.
    
    3. ACCESS CONTROLS
    Organizations are required to implement multi-factor authentication
    for all critical systems. Access controls must be reviewed quarterly.
    
    4. INCIDENT RESPONSE
    The security team shall maintain an incident response plan.
    Response procedures must be tested semi-annually.
    
    5. TRAINING AND AWARENESS
    All employees must complete annual privacy training.
    Training records shall be maintained for compliance verification.
    
    6. AUDIT AND MONITORING
    Organizations shall conduct internal audits on compliance activities.
    Audit reports must be submitted to management within 30 days.
    
    7. DOCUMENTATION
    All compliance activities shall be documented and archived.
    Records must be retained for at least 7 years.
    """

    try:
        extractor = get_extractor()
        result = extractor.extract_obligations(comprehensive_text)
        obligations = result.get("obligations", [])

        print(f"\n✓ Analysis Results:")
        print(f"  Total Obligations: {len(obligations)}")

        # Categorize
        categories = {}
        for ob in obligations:
            cat = ob['category']
            categories[cat] = categories.get(cat, 0) + 1

        print(f"\n  By Category:")
        for cat, count in sorted(categories.items()):
            print(f"    - {cat}: {count}")

        # Prioritize
        priorities = {}
        for ob in obligations:
            pri = ob['priority']
            priorities[pri] = priorities.get(pri, 0) + 1

        print(f"\n  By Priority:")
        for pri in ["critical", "high", "medium", "low"]:
            if pri in priorities:
                print(f"    - {pri}: {priorities[pri]}")

        # Sample obligations
        print(f"\n  Sample Obligations:")
        for ob in obligations[:3]:
            print(f"\n    {ob['obligation_id']}: {ob['obligation_text'][:60]}...")
            print(f"    Priority: {ob['priority']} | Team: {ob['responsible_team']}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")


# ============================================================================
# Main Test Suite
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  RegLoop AI - Obligation Extraction Engine - Test Suite".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    try:
        test_direct_extraction()
        test_category_classification()
        test_priority_assessment()
        test_duplicate_detection()
        test_full_workflow()
        # test_database_integration()  # Uncomment to test with database

        print("\n" + "="*70)
        print("✓ ALL TESTS COMPLETED")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()
