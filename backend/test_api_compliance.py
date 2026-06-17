"""API integration test for compliance-summary endpoint."""

import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from database.db import init_db, SessionLocal
from database.models import Document, DocumentType, Obligation, PriorityLevel, ObligationCategory, GapAnalysis
from main import app

def setup_test_data():
    """Create test data in database."""
    db = SessionLocal()
    
    # Clear existing data
    db.query(GapAnalysis).delete()
    db.query(Obligation).delete()
    db.query(Document).delete()
    db.commit()
    
    # Create test document
    doc = Document(
        filename="test_regulation.pdf",
        document_type=DocumentType.REGULATION,
        text_length=1000,
        raw_text="Sample regulation text"
    )
    db.add(doc)
    db.flush()
    
    # Create test obligations with various priorities and categories
    test_data = [
        # HIGH priority obligations
        ("OBL_0001", "System shall support upgrades.", ObligationCategory.OPERATIONAL, PriorityLevel.HIGH),
        ("OBL_0002", "Data shall be encrypted.", ObligationCategory.SECURITY, PriorityLevel.HIGH),
        ("OBL_0003", "Incidents shall be reported.", ObligationCategory.REPORTING, PriorityLevel.HIGH),
        ("OBL_0004", "Compliance requirements shall be met.", ObligationCategory.COMPLIANCE, PriorityLevel.HIGH),
        
        # MEDIUM priority obligations
        ("OBL_0005", "Systems must monitor performance.", ObligationCategory.OPERATIONAL, PriorityLevel.MEDIUM),
        ("OBL_0006", "Access controls must be implemented.", ObligationCategory.SECURITY, PriorityLevel.MEDIUM),
        ("OBL_0007", "Status must be reported.", ObligationCategory.REPORTING, PriorityLevel.MEDIUM),
        
        # LOW priority obligations
        ("OBL_0008", "Operations should review logs.", ObligationCategory.OPERATIONAL, PriorityLevel.LOW),
        ("OBL_0009", "Audit trails should be recorded.", ObligationCategory.COMPLIANCE, PriorityLevel.LOW),
    ]
    
    for obl_id, text, category, priority in test_data:
        ob = Obligation(
            document_id=doc.id,
            obligation_id=obl_id,
            obligation_text=text,
            category=category,
            priority=priority,
            responsible_team="IT"
        )
        db.add(ob)
        db.flush()
        
        gap = GapAnalysis(
            obligation_id=ob.id,
            status="open",
            coverage_score=0.0
        )
        db.add(gap)
    
    db.commit()
    db.close()


def test_compliance_summary_endpoint():
    """Test the compliance-summary endpoint."""
    
    # Initialize database and setup test data
    init_db()
    setup_test_data()
    
    # Create test client
    client = TestClient(app)
    
    print("\n" + "="*80)
    print("API INTEGRATION TEST: /compliance-summary")
    print("="*80)
    
    # Make request to endpoint
    print("\nSending GET /compliance-summary...")
    response = client.get("/compliance-summary")
    
    # Check status code
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("[OK] Status code is 200")
    
    # Parse response
    data = response.json()
    print("\nResponse received successfully")
    
    # Validate response structure
    required_fields = ["overall_compliance_score", "total_obligations", "categories", "priority_breakdown"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"
    print(f"[OK] All required fields present: {required_fields}")
    
    # Validate values
    print(f"\nResponse Data:")
    print(f"  Overall Compliance Score: {data['overall_compliance_score']}")
    print(f"  Total Obligations: {data['total_obligations']}")
    
    assert data['total_obligations'] == 9, f"Expected 9 obligations, got {data['total_obligations']}"
    print("[OK] Total obligations count is correct")
    
    # Check overall score is in valid range (0-100)
    score = data['overall_compliance_score']
    assert 0 <= score <= 100, f"Score {score} out of valid range [0, 100]"
    print(f"[OK] Overall score is in valid range: {score}")
    
    # Validate categories
    print(f"\nCategories ({len(data['categories'])} total):")
    categories_found = []
    for category in data['categories']:
        assert "category" in category, "Missing 'category' field"
        assert "total_obligations" in category, "Missing 'total_obligations' field"
        assert "average_coverage" in category, "Missing 'average_coverage' field"
        
        cat_name = category['category']
        total = category['total_obligations']
        avg = category['average_coverage']
        categories_found.append(cat_name)
        
        print(f"  {cat_name:15} - {total:2} obligations, avg coverage: {avg:6.1f}")
        
        # Validate coverage is in valid range
        assert 0 <= avg <= 100, f"Coverage {avg} out of range for {cat_name}"
    
    print(f"[OK] Categories are valid and properly formatted")
    
    # Validate priority breakdown
    pb = data['priority_breakdown']
    print(f"\nPriority Breakdown:")
    print(f"  HIGH:   {pb['high']:2} obligations, avg coverage: {pb['high_coverage']:6.1f}")
    print(f"  MEDIUM: {pb['medium']:2} obligations, avg coverage: {pb['medium_coverage']:6.1f}")
    print(f"  LOW:    {pb['low']:2} obligations, avg coverage: {pb['low_coverage']:6.1f}")
    
    # Verify counts
    total_by_priority = pb['high'] + pb['medium'] + pb['low']
    assert total_by_priority == data['total_obligations'], "Priority breakdown count mismatch"
    print("[OK] Priority counts sum to total obligations")
    
    # Verify coverage values match expected scores
    assert pb['high_coverage'] == 90.0, f"HIGH coverage should be 90, got {pb['high_coverage']}"
    assert pb['medium_coverage'] == 70.0, f"MEDIUM coverage should be 70, got {pb['medium_coverage']}"
    assert pb['low_coverage'] == 50.0, f"LOW coverage should be 50, got {pb['low_coverage']}"
    print("[OK] Coverage scores match expected values (90/70/50)")
    
    # Calculate expected overall score
    expected_score = (pb['high'] * 90 + pb['medium'] * 70 + pb['low'] * 50) / data['total_obligations']
    actual_score = data['overall_compliance_score']
    assert abs(expected_score - actual_score) < 0.1, f"Score calculation mismatch"
    print(f"[OK] Overall score calculation is correct: {actual_score}")
    
    print("\n" + "="*80)
    print("ALL TESTS PASSED!")
    print("="*80)
    print(f"\nSummary:")
    print(f"  Overall Compliance Score: {data['overall_compliance_score']}")
    print(f"  Total Obligations: {data['total_obligations']}")
    print(f"  Categories Analyzed: {len(data['categories'])}")
    print(f"  Priority Distribution: HIGH={pb['high']}, MEDIUM={pb['medium']}, LOW={pb['low']}")
    print()


if __name__ == "__main__":
    try:
        test_compliance_summary_endpoint()
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
