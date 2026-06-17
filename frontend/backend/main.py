from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import shutil
import pdfplumber
import logging

from database.db import get_db, init_db
from database.models import Document, DocumentType, Obligation, GapAnalysis
from database.schemas import DocumentResponse
from services.obligation_extractor import get_extractor
from services.compliance_scorer import get_scorer

logger = logging.getLogger(__name__)

app = FastAPI(
    title="RegLoop AI",
    version="1.0.0",
    description="Closed-Loop Regulatory Execution Platform"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    init_db()
    print("✓ Database initialized")

@app.get("/")
def root():
    return {"message": "RegLoop AI API Running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = ""

    if file.filename.lower().endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() or ""
                extracted_text += "\n"

    # Save document to database
    doc = Document(
        filename=file.filename,
        document_type=DocumentType.OTHER,
        text_length=len(extracted_text),
        raw_text=extracted_text
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "success": True,
        "document_id": doc.id,
        "filename": file.filename,
        "text_length": len(extracted_text),
        "preview": extracted_text[:500]
    }


# ============================================================================
# Document Endpoints
# ============================================================================

@app.get("/documents")
async def get_documents(db: Session = Depends(get_db)):
    """Get all uploaded documents."""
    documents = db.query(Document).all()
    return {
        "total": len(documents),
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "document_type": doc.document_type,
                "uploaded_at": doc.uploaded_at,
                "text_length": doc.text_length,
                "obligations_count": len(doc.obligations)
            }
            for doc in documents
        ]
    }


@app.get("/documents/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document with its obligations."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type,
        "uploaded_at": doc.uploaded_at,
        "text_length": doc.text_length,
        "obligations": [
            {
                "id": ob.id,
                "obligation_id": ob.obligation_id,
                "obligation_text": ob.obligation_text,
                "category": ob.category,
                "priority": ob.priority,
                "responsible_team": ob.responsible_team,
                "deadline_or_frequency": ob.deadline_or_frequency,
                "gap_analysis": {
                    "status": ob.gap_analysis.status,
                    "coverage_score": ob.gap_analysis.coverage_score,
                    "gap_summary": ob.gap_analysis.gap_summary
                } if ob.gap_analysis else None
            }
            for ob in doc.obligations
        ]
    }


# ============================================================================
# Obligations Endpoints
# ============================================================================

@app.get("/obligations")
async def get_obligations(
    priority: str = None,
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get obligations with optional filtering."""
    query = db.query(Obligation)
    
    if priority:
        query = query.filter(Obligation.priority == priority)
    if category:
        query = query.filter(Obligation.category == category)
    
    obligations = query.all()
    return {
        "total": len(obligations),
        "obligations": [
            {
                "id": ob.id,
                "obligation_id": ob.obligation_id,
                "obligation_text": ob.obligation_text,
                "category": ob.category,
                "priority": ob.priority,
                "responsible_team": ob.responsible_team
            }
            for ob in obligations
        ]
    }


@app.post("/documents/{document_id}/obligations")
async def create_obligation(
    document_id: int,
    obligation_data: dict,
    db: Session = Depends(get_db)
):
    """Create an obligation for a document (from Claude analysis)."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    ob = Obligation(
        document_id=document_id,
        **obligation_data
    )
    db.add(ob)
    db.commit()
    db.refresh(ob)
    
    return {
        "success": True,
        "obligation_id": ob.id,
        "message": "Obligation created successfully"
    }


# ============================================================================
# Gap Analysis Endpoints
# ============================================================================

@app.get("/gap-analysis")
async def get_gap_analysis(status: str = None, db: Session = Depends(get_db)):
    """Get gap analysis records with optional status filtering."""
    query = db.query(GapAnalysis)
    
    if status:
        query = query.filter(GapAnalysis.status == status)
    
    gaps = query.all()
    return {
        "total": len(gaps),
        "gaps": [
            {
                "id": gap.id,
                "obligation_id": gap.obligation_id,
                "status": gap.status,
                "coverage_score": gap.coverage_score,
                "gap_summary": gap.gap_summary,
                "recommended_action": gap.recommended_action
            }
            for gap in gaps
        ]
    }


@app.get("/compliance-summary")
async def get_compliance_summary(db: Session = Depends(get_db)):
    """Get compliance summary with coverage scores.
    
    Returns overall compliance score and per-category breakdown:
    - overall_compliance_score: Average across all obligations (0-100)
    - categories: Per-category statistics with coverage scores
    - priority_breakdown: Statistics by priority level
    
    Scoring Rules (MVP):
    - High Priority: 90 points
    - Medium Priority: 70 points
    - Low Priority: 50 points
    """
    scorer = get_scorer()
    
    # Get comprehensive compliance report
    compliance_report = scorer.calculate_overall_compliance(db)
    
    return compliance_report


# ============================================================================
# Obligation Analysis Endpoints
# ============================================================================

@app.post("/documents/{document_id}/analyze")
async def analyze_document(document_id: int, db: Session = Depends(get_db)):
    """
    Analyze document and extract regulatory obligations.
    
    Workflow:
    1. Load document from database
    2. Extract obligations using free local extractor
    3. Save obligations to database
    4. Return summary
    
    Args:
        document_id: ID of the document to analyze
        db: Database session
        
    Returns:
        Dict with document_id and obligations_created count
        
    Raises:
        HTTPException: If document not found or extraction fails
    """
    logger.info(f"Starting analysis for document {document_id}")
    
    # Load document
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        logger.error(f"Document {document_id} not found")
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not doc.raw_text:
        logger.error(f"Document {document_id} has no text content")
        raise HTTPException(status_code=400, detail="Document has no extracted text")
    
    try:
        # Extract obligations
        extractor = get_extractor()
        result = extractor.extract_obligations(doc.raw_text)
        obligations_data = result.get("obligations", [])
        
        logger.info(f"Extracted {len(obligations_data)} obligations from document {document_id}")
        
        # Save to database
        created_count = 0
        for idx, obligation_dict in enumerate(obligations_data, 1):
            try:
                obligation = Obligation(
                    document_id=document_id,
                    obligation_id=obligation_dict.get("obligation_id", f"OBL_{idx:04d}"),
                    obligation_text=obligation_dict.get("obligation_text", ""),
                    category=obligation_dict.get("category", "other"),
                    priority=obligation_dict.get("priority", "medium"),
                    responsible_team=obligation_dict.get("responsible_team", "Compliance"),
                    evidence_required=obligation_dict.get("evidence_required", ""),
                    deadline_or_frequency=obligation_dict.get("deadline_or_frequency", "As required"),
                    risk_if_not_met=obligation_dict.get("risk_if_not_met", "")
                )
                db.add(obligation)
                created_count += 1
                
            except Exception as e:
                logger.error(f"Error creating obligation {idx}: {str(e)}")
                continue
        
        # Commit all obligations
        db.commit()
        logger.info(f"Successfully saved {created_count} obligations for document {document_id}")
        
        return {
            "success": True,
            "document_id": document_id,
            "obligations_created": created_count,
            "message": f"Successfully analyzed document and created {created_count} obligations"
        }
        
    except ValueError as e:
        logger.error(f"Extraction validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Extraction failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/documents/{document_id}/analyze-and-gaps")
async def analyze_document_with_gaps(document_id: int, db: Session = Depends(get_db)):
    """
    Analyze document and create gap analysis records.
    
    Workflow:
    1. Load document
    2. Extract obligations
    3. Save obligations
    4. Create gap analysis with initial coverage 0%
    5. Return summary
    
    Args:
        document_id: ID of the document to analyze
        db: Database session
        
    Returns:
        Dict with document_id, obligations_created, and gaps_created
    """
    logger.info(f"Starting analysis with gaps for document {document_id}")
    
    # Load document
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not doc.raw_text:
        raise HTTPException(status_code=400, detail="Document has no extracted text")
    
    try:
        # Extract obligations
        extractor = get_extractor()
        result = extractor.extract_obligations(doc.raw_text)
        obligations_data = result.get("obligations", [])
        
        created_obligations = []
        gaps_created = 0
        
        # Save obligations and create gaps
        for idx, obligation_dict in enumerate(obligations_data, 1):
            try:
                obligation = Obligation(
                    document_id=document_id,
                    obligation_id=obligation_dict.get("obligation_id", f"OBL_{idx:04d}"),
                    obligation_text=obligation_dict.get("obligation_text", ""),
                    category=obligation_dict.get("category", "other"),
                    priority=obligation_dict.get("priority", "medium"),
                    responsible_team=obligation_dict.get("responsible_team", "Compliance"),
                    evidence_required=obligation_dict.get("evidence_required", ""),
                    deadline_or_frequency=obligation_dict.get("deadline_or_frequency", "As required"),
                    risk_if_not_met=obligation_dict.get("risk_if_not_met", "")
                )
                db.add(obligation)
                db.flush()
                created_obligations.append(obligation)
                
                # Create gap analysis with 0% coverage
                gap = GapAnalysis(
                    obligation_id=obligation.id,
                    status="open",
                    coverage_score=0.0,
                    gap_summary=f"Gap analysis initiated. Evidence required: {obligation.evidence_required}",
                    recommended_action=f"Gather evidence to demonstrate compliance with: {obligation.obligation_text[:100]}..."
                )
                db.add(gap)
                gaps_created += 1
                
            except Exception as e:
                logger.error(f"Error creating obligation {idx}: {str(e)}")
                continue
        
        db.commit()
        logger.info(f"Created {len(created_obligations)} obligations and {gaps_created} gaps")
        
        return {
            "success": True,
            "document_id": document_id,
            "obligations_created": len(created_obligations),
            "gaps_created": gaps_created,
            "message": f"Successfully analyzed document and created {len(created_obligations)} obligations with gap analyses"
        }
        
    except ValueError as e:
        logger.error(f"Extraction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Extraction failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")