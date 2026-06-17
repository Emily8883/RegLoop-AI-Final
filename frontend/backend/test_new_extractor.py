"""Quick test of the new obligation extractor."""

import logging
from services.obligation_extractor import get_extractor

# Test with sample regulatory text
sample_text = """
REGULATORY COMPLIANCE POLICY

1. Introduction
This policy establishes the requirements for regulatory compliance across all operations.

2. Security Requirements
The system shall support strong authentication mechanisms. All authentication credentials must be encrypted using industry-standard algorithms. Organizations must implement comprehensive security controls for data protection.

3. Reporting Obligations
Vendors shall report any security incidents within 24 hours. The compliance team is responsible for maintaining audit logs. Organizations are required to submit quarterly compliance reports to the regulatory authority.

4. Documentation Requirements
Each facility must maintain detailed records of all regulatory reviews. Documentation of compliance procedures shall be archived for at least 7 years. The operations team is responsible for performing monthly system maintenance and monitoring.

5. Audit and Compliance
All audit findings require immediate corrective action. Regulatory bodies must conduct annual compliance assessments. The organization shall ensure all employees receive training on compliance policies.

Page 5
"""

try:
    extractor = get_extractor()
    result = extractor.extract_obligations(sample_text)
    
    print("[OK] Extraction successful!")
    print(f"[OK] Extracted {len(result['obligations'])} obligations\n")
    
    for i, ob in enumerate(result['obligations'], 1):
        print(f"{i}. {ob['obligation_id']}")
        print(f"   Text: {ob['obligation_text'][:70]}...")
        print(f"   Category: {ob['category']}")
        print(f"   Priority: {ob['priority']}")
        print(f"   Team: {ob['responsible_team']}")
        print(f"   Evidence: {ob['evidence_required'][:50]}...")
        print()
        
except Exception as e:
    print(f"[FAIL] Extraction failed: {e}")
    import traceback
    traceback.print_exc()
