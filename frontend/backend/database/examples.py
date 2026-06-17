"""Examples of database operations for RegLoop AI."""

from datetime import datetime, timedelta
from database.db import SessionLocal
from database.models import Document, Obligation, GapAnalysis, DocumentType, ObligationCategory, PriorityLevel, GapStatus


# ============================================================================
# INSERTION EXAMPLES
# ============================================================================

def example_insert_document():
    """Example: Insert a new document."""
    db = SessionLocal()
    
    try:
        # Create a document
        doc = Document(
            filename="GDPR_Regulation_2023.pdf",
            document_type=DocumentType.REGULATION,
            text_length=5420,
            raw_text="Full text of the GDPR regulation...",
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        print(f"✓ Document created: {doc}")
        return doc.id
        
    finally:
        db.close()


def example_insert_obligations():
    """Example: Insert obligations for a document."""
    db = SessionLocal()
    
    try:
        document_id = 1  # Assume document exists
        
        # Create multiple obligations from Claude analysis
        obligations_data = [
            {
                "obligation_id": "GDPR_001",
                "obligation_text": "Organizations must implement data protection by design.",
                "category": ObligationCategory.DOCUMENTATION,
                "priority": PriorityLevel.CRITICAL,
                "responsible_team": "Data Protection Officer",
                "evidence_required": "Certification of implementation, process documentation",
                "deadline_or_frequency": "Immediate, ongoing quarterly reviews",
                "risk_if_not_met": "Fines up to 4% of annual revenue",
            },
            {
                "obligation_id": "GDPR_002",
                "obligation_text": "Data breach notification within 72 hours.",
                "category": ObligationCategory.REPORTING,
                "priority": PriorityLevel.CRITICAL,
                "responsible_team": "Security & Compliance Team",
                "evidence_required": "Incident response plan, notification logs",
                "deadline_or_frequency": "72 hours from discovery",
                "risk_if_not_met": "Significant regulatory penalties",
            },
            {
                "obligation_id": "GDPR_003",
                "obligation_text": "Maintain records of processing activities.",
                "category": ObligationCategory.DOCUMENTATION,
                "priority": PriorityLevel.HIGH,
                "responsible_team": "Data Governance Team",
                "evidence_required": "Processing records, audit logs",
                "deadline_or_frequency": "Continuously maintained",
                "risk_if_not_met": "Regulatory inspection failures",
            },
        ]
        
        for ob_data in obligations_data:
            obligation = Obligation(
                document_id=document_id,
                **ob_data
            )
            db.add(obligation)
        
        db.commit()
        print(f"✓ Created {len(obligations_data)} obligations")
        
    finally:
        db.close()


def example_insert_gap_analysis():
    """Example: Insert gap analysis for obligations."""
    db = SessionLocal()
    
    try:
        # Assume obligations exist with IDs 1, 2, 3
        gap_data = [
            {
                "obligation_id": 1,
                "status": GapStatus.OPEN,
                "coverage_score": 45.0,
                "gap_summary": "Current implementation lacks formal DPbD framework. Need governance structure.",
                "recommended_action": "1. Establish DPbD governance 2. Document processes 3. Train team",
            },
            {
                "obligation_id": 2,
                "status": GapStatus.IN_PROGRESS,
                "coverage_score": 70.0,
                "gap_summary": "Incident response plan exists but 72-hour notification needs automation.",
                "recommended_action": "Implement automated breach notification system",
            },
            {
                "obligation_id": 3,
                "status": GapStatus.RESOLVED,
                "coverage_score": 95.0,
                "gap_summary": "Processing records system implemented and functioning well.",
                "recommended_action": "Continue quarterly audits",
            },
        ]
        
        for gap in gap_data:
            gap_analysis = GapAnalysis(**gap)
            db.add(gap_analysis)
        
        db.commit()
        print(f"✓ Created {len(gap_data)} gap analyses")
        
    finally:
        db.close()


# ============================================================================
# QUERY EXAMPLES
# ============================================================================

def example_query_all_documents():
    """Example: Retrieve all documents."""
    db = SessionLocal()
    
    try:
        documents = db.query(Document).all()
        print(f"\n📄 All Documents ({len(documents)}):")
        for doc in documents:
            print(f"  - {doc.filename} ({doc.document_type}) - {len(doc.obligations)} obligations")
        
    finally:
        db.close()


def example_query_document_with_obligations():
    """Example: Get a document with all its obligations."""
    db = SessionLocal()
    
    try:
        document = db.query(Document).filter(Document.id == 1).first()
        
        if document:
            print(f"\n📋 Document: {document.filename}")
            print(f"   Type: {document.document_type}")
            print(f"   Uploaded: {document.uploaded_at}")
            print(f"   Obligations: {len(document.obligations)}")
            
            for ob in document.obligations:
                print(f"     • {ob.obligation_id}: {ob.obligation_text[:50]}...")
                if ob.gap_analysis:
                    print(f"       → Gap Status: {ob.gap_analysis.status} (Coverage: {ob.gap_analysis.coverage_score}%)")
        
    finally:
        db.close()


def example_query_obligations_by_priority():
    """Example: Get all critical and high priority obligations."""
    db = SessionLocal()
    
    try:
        obligations = db.query(Obligation).filter(
            Obligation.priority.in_([PriorityLevel.CRITICAL, PriorityLevel.HIGH])
        ).all()
        
        print(f"\n🚨 Critical & High Priority Obligations ({len(obligations)}):")
        for ob in obligations:
            print(f"  • [{ob.priority}] {ob.obligation_id}: {ob.obligation_text[:60]}...")
            print(f"    Team: {ob.responsible_team}, Deadline: {ob.deadline_or_frequency}")
        
    finally:
        db.close()


def example_query_open_gaps():
    """Example: Get all open gaps requiring action."""
    db = SessionLocal()
    
    try:
        gaps = db.query(GapAnalysis).filter(
            GapAnalysis.status == GapStatus.OPEN
        ).all()
        
        print(f"\n⚠️  Open Gaps ({len(gaps)}):")
        for gap in gaps:
            ob = gap.obligation
            print(f"  • Obligation: {ob.obligation_id}")
            print(f"    Coverage: {gap.coverage_score}%")
            print(f"    Action: {gap.recommended_action}")
        
    finally:
        db.close()


def example_query_compliance_summary():
    """Example: Get compliance summary by category."""
    db = SessionLocal()
    
    try:
        from sqlalchemy import func
        
        summary = db.query(
            Obligation.category,
            func.count(Obligation.id).label("total"),
            func.avg(GapAnalysis.coverage_score).label("avg_coverage")
        ).outerjoin(GapAnalysis).group_by(Obligation.category).all()
        
        print(f"\n📊 Compliance Summary by Category:")
        print(f"  {'Category':<20} {'Total':<8} {'Avg Coverage':<15}")
        print(f"  {'-'*43}")
        
        for category, total, avg_coverage in summary:
            coverage = f"{avg_coverage:.1f}%" if avg_coverage else "N/A"
            print(f"  {category:<20} {total:<8} {coverage:<15}")
        
    finally:
        db.close()


def example_query_high_risk_items():
    """Example: Find high-risk items with low coverage."""
    db = SessionLocal()
    
    try:
        high_risk = db.query(Obligation, GapAnalysis).join(
            GapAnalysis, Obligation.id == GapAnalysis.obligation_id
        ).filter(
            (Obligation.priority == PriorityLevel.CRITICAL) &
            (GapAnalysis.coverage_score < 60)
        ).all()
        
        print(f"\n🔴 High Risk Items (Critical + <60% Coverage):")
        for ob, gap in high_risk:
            print(f"  • {ob.obligation_id}: {ob.obligation_text[:60]}...")
            print(f"    Coverage: {gap.coverage_score}% | Action: {gap.recommended_action}")
        
    finally:
        db.close()


def example_update_gap_status():
    """Example: Update gap analysis status."""
    db = SessionLocal()
    
    try:
        gap = db.query(GapAnalysis).filter(GapAnalysis.id == 1).first()
        
        if gap:
            old_status = gap.status
            gap.status = GapStatus.RESOLVED
            gap.coverage_score = 100.0
            db.commit()
            
            print(f"\n✅ Updated Gap Analysis #{gap.id}:")
            print(f"   Status: {old_status} → {gap.status}")
            print(f"   Coverage: {gap.coverage_score}%")
        
    finally:
        db.close()


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("RegLoop AI - Database Examples")
    print("=" * 60)
    
    # Uncomment to run examples
    # example_insert_document()
    # example_insert_obligations()
    # example_insert_gap_analysis()
    
    example_query_all_documents()
    example_query_document_with_obligations()
    example_query_obligations_by_priority()
    example_query_open_gaps()
    example_query_compliance_summary()
    example_query_high_risk_items()
    # example_update_gap_status()
    
    print("\n" + "=" * 60)
