from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import os
import shutil
import pdfplumber
import logging
from datetime import datetime

from database.db import get_db, init_db
from database.models import Document, DocumentType, Obligation, GapAnalysis
from database.policy_models import PolicyPullRequest, PolicyReviewAction, ReviewAction
from database.schemas import DocumentResponse
from services.obligation_extractor import get_extractor
from services.enhanced_obligation_extractor import get_enhanced_extractor
from services.compliance_scorer import get_scorer
from services.gemini_service import GeminiService
from services.policy_pr_generator import get_pr_generator
from services.policy_mapper import get_policy_mapper
from services.gap_analysis_ai import get_gap_analysis_ai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Lifespan event handler (modern FastAPI pattern)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    print("✓ Database initialized")
    logger.info("Database initialization complete")
    yield

app = FastAPI(
    title="RegLoop AI",
    version="1.0.0",
    description="Closed-Loop Regulatory Execution Platform",
    lifespan=lifespan
)

# Add CORS middleware - Allow frontend at localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "RegLoop AI API Running"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    document_type: str = Form("other"),
    db: Session = Depends(get_db)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = ""

    if file.filename.lower().endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() or ""
                extracted_text += "\n"

    try:
        normalized_document_type = DocumentType(document_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid document_type. Use regulation, policy, compliance, or other."
        )

    # Save document to database
    doc = Document(
        filename=file.filename,
        document_type=normalized_document_type,
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
        "document_type": doc.document_type,
        "text_length": len(extracted_text),
        "preview": extracted_text[:500]
    }


@app.post("/upload/responsibility-matrix")
async def upload_responsibility_matrix(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload responsibility matrix (CSV file) for team assignments.
    
    Expected CSV format:
    obligation_id,responsible_team,owner_email
    OBL_001,Compliance,john@company.com
    OBL_002,Security,jane@company.com
    """
    try:
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(status_code=400, detail="File must be in CSV format")
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse and process CSV
        import csv
        
        responsibility_map = {}
        row_count = 0
        
        with open(file_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                obligation_id = row.get("obligation_id", "").strip()
                responsible_team = row.get("responsible_team", "").strip()
                owner_email = row.get("owner_email", "").strip()
                
                if obligation_id:
                    responsibility_map[obligation_id] = {
                        "team": responsible_team,
                        "email": owner_email
                    }
                    row_count += 1
        
        logger.info(f"✓ Loaded responsibility matrix: {row_count} entries from {file.filename}")
        
        return {
            "success": True,
            "filename": file.filename,
            "rows_loaded": row_count,
            "responsibility_map": responsibility_map,
            "message": f"Successfully loaded {row_count} responsibility assignments"
        }
    
    except Exception as e:
        logger.error(f"Error uploading responsibility matrix: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV upload failed: {str(e)}")


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
                "confidence_score": ob.confidence_score,
                "source_citation": ob.source_citation,
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
                "responsible_team": ob.responsible_team,
                "confidence_score": ob.confidence_score,
                "source_citation": ob.source_citation
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
                "risk_level": gap.obligation.priority.value if gap.obligation and hasattr(gap.obligation.priority, "value") else str(gap.obligation.priority).lower() if gap.obligation else "medium",
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
        # Extract obligations using enhanced AI-powered extractor
        enhanced_extractor = get_enhanced_extractor()
        result = enhanced_extractor.extract_obligations(doc.raw_text)
        obligations_data = result.get("obligations", [])
        
        logger.info(f"Extracted {len(obligations_data)} obligations from document {document_id}")
        
        # Save to database with confidence scores and citations
        created_count = 0
        for idx, obligation_dict in enumerate(obligations_data, 1):
            try:
                obligation = Obligation(
                    document_id=document_id,
                    obligation_id=obligation_dict.get("obligation_id", f"OBL_{idx:04d}"),
                    obligation_text=obligation_dict.get("obligation_text", ""),
                    category=obligation_dict.get("category", "compliance"),
                    priority=obligation_dict.get("priority", "medium"),
                    responsible_team=obligation_dict.get("responsible_team", "Compliance"),
                    evidence_required=obligation_dict.get("evidence_required", ""),
                    deadline_or_frequency=obligation_dict.get("deadline_or_frequency", "As required"),
                    risk_if_not_met=obligation_dict.get("risk_if_not_met", ""),
                    confidence_score=float(obligation_dict.get("confidence_score", 0.75)),
                    source_citation=obligation_dict.get("source_citation", "")
                )
                db.add(obligation)
                created_count += 1
                
            except Exception as e:
                logger.error(f"Error creating obligation {idx}: {str(e)}")
                continue
        
        # Commit all obligations
        db.commit()
        logger.info(f"Successfully saved {created_count} obligations with confidence scores")
        
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
        # Extract obligations using enhanced AI-powered extractor
        enhanced_extractor = get_enhanced_extractor()
        result = enhanced_extractor.extract_obligations(doc.raw_text)
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
                    category=obligation_dict.get("category", "compliance"),
                    priority=obligation_dict.get("priority", "medium"),
                    responsible_team=obligation_dict.get("responsible_team", "Compliance"),
                    evidence_required=obligation_dict.get("evidence_required", ""),
                    deadline_or_frequency=obligation_dict.get("deadline_or_frequency", "As required"),
                    risk_if_not_met=obligation_dict.get("risk_if_not_met", ""),
                    confidence_score=float(obligation_dict.get("confidence_score", 0.75)),
                    source_citation=obligation_dict.get("source_citation", "")
                )
                db.add(obligation)
                db.flush()
                created_obligations.append(obligation)
                
                # Create gap analysis with 0% coverage
                gap = GapAnalysis(
                    obligation_id=obligation.id,
                    status="open",
                    coverage_score=0.0,
                    gap_summary=f"Gap analysis initiated. Evidence required: {obligation.evidence_required}. Confidence: {obligation.confidence_score:.1%}",
                    recommended_action=f"Gather evidence to demonstrate compliance with: {obligation.obligation_text[:100]}... [Citation: {obligation.source_citation}]"
                )
                db.add(gap)
                gaps_created += 1
                
            except Exception as e:
                logger.error(f"Error creating obligation {idx}: {str(e)}")
                continue
        
        db.commit()
        logger.info(f"Created {len(created_obligations)} obligations and {gaps_created} gaps with AI enhancement")
        
        return {
            "success": True,
            "document_id": document_id,
            "obligations_created": len(created_obligations),
            "gaps_created": gaps_created,
            "ai_enhanced": True,
            "message": f"Successfully analyzed document with AI: {len(created_obligations)} obligations extracted with confidence scores and citations"
        }
        
    except ValueError as e:
        logger.error(f"Extraction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Extraction failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ============================================================================
# AI-Powered Analysis Endpoint (using Gemini API)
# ============================================================================

@app.post("/documents/{document_id}/ai-analyze")
async def ai_analyze_document(document_id: int, db: Session = Depends(get_db)):
    """
    AI-powered document analysis using Gemini API.
    
    Uses Google Generative AI to provide enhanced obligation extraction
    and analysis with natural language understanding.
    
    Workflow:
    1. Check if Gemini API is configured
    2. Load document from database
    3. Use Gemini to analyze and extract obligations
    4. Save obligations to database
    5. Return AI analysis summary
    
    Args:
        document_id: ID of the document to analyze with AI
        db: Database session
        
    Returns:
        Dict with document_id, obligations_created, and ai_analysis
        
    Raises:
        HTTPException: If Gemini API is not configured or document not found
    """
    logger.info(f"Starting AI analysis for document {document_id}")
    
    # Check if Gemini API is available
    if not GeminiService.is_available():
        logger.warning("Gemini API not configured")
        raise HTTPException(
            status_code=503,
            detail="AI analysis unavailable: Gemini API not configured. Please ensure GEMINI_API_KEY is set in .env file."
        )
    
    # Load document
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        logger.error(f"Document {document_id} not found")
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not doc.raw_text:
        logger.error(f"Document {document_id} has no text content")
        raise HTTPException(status_code=400, detail="Document has no extracted text")
    
    try:
        # Prepare text for Gemini (limit to first 3000 characters to avoid token limits)
        document_excerpt = doc.raw_text[:3000]
        
        # Create detailed prompt for Gemini
        prompt = f"""Analyze the following regulatory document and extract all compliance obligations.

For each obligation found, provide:
1. The exact obligation text
2. Category (choose from: operational, reporting, security, compliance, other)
3. Priority level (high, medium, low)
4. Responsible team (e.g., Finance, Compliance, Operations, HR, IT, Management)
5. Deadline or frequency (e.g., "Monthly", "Annual", "As required")
6. Evidence required (what proof of compliance is needed)

Document Text:
{document_excerpt}

Format your response as a JSON array with objects containing these exact fields:
- obligation_text
- category
- priority
- responsible_team
- deadline_or_frequency
- evidence_required

Only return valid JSON, no other text."""

        logger.info("Sending document to Gemini API for analysis...")
        
        # Call Gemini API
        ai_response = GeminiService.generate_text(prompt)
        logger.info("✓ Received response from Gemini API")
        
        # Parse and save obligations
        created_count = 0
        ai_analysis = None
        
        try:
            # Try to extract JSON from response
            import json
            import re
            
            # Find JSON in response
            json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
            if json_match:
                obligations_data = json.loads(json_match.group())
                ai_analysis = ai_response
                
                # Save obligations from Gemini analysis
                for idx, obligation_dict in enumerate(obligations_data, 1):
                    try:
                        obligation = Obligation(
                            document_id=document_id,
                            obligation_id=obligation_dict.get("obligation_id", f"AI_OBL_{idx:04d}"),
                            obligation_text=obligation_dict.get("obligation_text", ""),
                            category=obligation_dict.get("category", "other"),
                            priority=obligation_dict.get("priority", "medium"),
                            responsible_team=obligation_dict.get("responsible_team", "Compliance"),
                            evidence_required=obligation_dict.get("evidence_required", ""),
                            deadline_or_frequency=obligation_dict.get("deadline_or_frequency", "As required"),
                            risk_if_not_met=f"AI identified obligation from regulatory analysis"
                        )
                        db.add(obligation)
                        created_count += 1
                    except Exception as e:
                        logger.error(f"Error creating obligation from Gemini {idx}: {str(e)}")
                        continue
                
                db.commit()
                logger.info(f"✓ Successfully saved {created_count} AI-identified obligations")
        
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON from Gemini response, storing raw analysis")
            ai_analysis = ai_response
        
        return {
            "success": True,
            "document_id": document_id,
            "obligations_created": created_count,
            "ai_powered": True,
            "api_used": "Google Generative AI (Gemini)",
            "ai_analysis": ai_analysis[:500] if ai_analysis else "No structured analysis available",
            "message": f"✓ AI analysis complete: Created {created_count} obligations using Gemini API"
        }
        
    except RuntimeError as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Gemini API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during AI analysis: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@app.get("/gemini/status")
async def gemini_status():
    """
    Check Gemini API configuration status.
    
    Returns:
        Dict with api_configured flag and status message
    """
    is_available = GeminiService.is_available()
    return {
        "api_configured": is_available,
        "status": "✓ Gemini API is configured and ready" if is_available else "✗ Gemini API not configured",
        "message": "You can use the /documents/{document_id}/ai-analyze endpoint" if is_available else "Please set GEMINI_API_KEY in .env file to enable AI features"
    }


# ============================================================================
# Policy Pull Request Endpoints (FR-5)
# ============================================================================

@app.post("/gaps/{gap_id}/create-pr")
async def create_policy_pr(
    gap_id: int,
    db: Session = Depends(get_db)
):
    """
    Create a policy pull request for a compliance gap.
    
    FR-5 Implementation: Generate policy amendment recommendations
    """
    logger.info(f"Creating PR for gap {gap_id}")
    
    # Load gap and obligation
    gap = db.query(GapAnalysis).filter(GapAnalysis.id == gap_id).first()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")
    
    obligation = gap.obligation
    if not obligation:
        raise HTTPException(status_code=404, detail="Associated obligation not found")
    
    try:
        # Generate PR using AI
        pr_generator = get_pr_generator()
        amendment_data = pr_generator.generate_pr_for_gap(
            gap_description=gap.gap_summary or "Compliance gap detected",
            obligation_text=obligation.obligation_text,
            regulatory_citation=obligation.source_citation or "Regulatory requirement",
            current_policy_text="",  # Would load from policy database
            priority=obligation.priority,
            category=obligation.category,
            responsible_team=obligation.responsible_team
        )
        
        # Create PR record
        pr = PolicyPullRequest(
            gap_analysis_id=gap_id,
            original_policy_text=amendment_data.get("original_policy_text", ""),
            proposed_amendment=amendment_data.get("proposed_amendment", ""),
            regulatory_citation=amendment_data.get("regulatory_citation", ""),
            gap_description=amendment_data.get("gap_description", ""),
            suggested_owner=amendment_data.get("suggested_owner", ""),
            risk_level=amendment_data.get("risk_level", "medium"),
            confidence_score=float(amendment_data.get("confidence_score", 0.75)),
            before_text=amendment_data.get("before_text", ""),
            after_text=amendment_data.get("after_text", ""),
            diff_summary=amendment_data.get("diff_summary", ""),
            status="pending"
        )
        
        db.add(pr)
        db.commit()
        db.refresh(pr)
        
        logger.info(f"✓ Created PR {pr.id} for gap {gap_id}")
        
        return {
            "success": True,
            "pr_id": pr.id,
            "gap_id": gap_id,
            "status": pr.status,
            "confidence_score": pr.confidence_score,
            "proposed_amendment": pr.proposed_amendment[:500],
            "message": "Policy pull request created successfully"
        }
    
    except Exception as e:
        logger.error(f"Error creating PR: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"PR creation failed: {str(e)}")


@app.get("/policy-prs")
async def get_policy_prs(
    status: str = None,
    gap_id: int = None,
    db: Session = Depends(get_db)
):
    """Get all policy pull requests with optional filtering."""
    query = db.query(PolicyPullRequest)
    
    if status:
        query = query.filter(PolicyPullRequest.status == status)
    if gap_id:
        query = query.filter(PolicyPullRequest.gap_analysis_id == gap_id)
    
    prs = query.all()
    
    return {
        "total": len(prs),
        "policy_prs": [
            {
                "id": pr.id,
                "gap_id": pr.gap_analysis_id,
                "status": pr.status,
                "risk_level": pr.risk_level,
                "confidence_score": pr.confidence_score,
                "regulatory_citation": pr.regulatory_citation,
                "suggested_owner": pr.suggested_owner,
                "gap_description": pr.gap_description,
                "proposed_amendment": pr.proposed_amendment,
                "original_policy_text": pr.original_policy_text,
                "before_text": pr.before_text,
                "after_text": pr.after_text,
                "diff_summary": pr.diff_summary,
                "created_at": pr.created_at.isoformat() if pr.created_at else None
            }
            for pr in prs
        ]
    }


@app.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and all related obligations/gaps."""
    doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        db.delete(doc)
        db.commit()
        return {
            "success": True,
            "document_id": document_id,
            "message": "Document deleted successfully"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.get("/policy-prs/{pr_id}")
async def get_policy_pr(pr_id: int, db: Session = Depends(get_db)):
    """Get detailed policy pull request."""
    pr = db.query(PolicyPullRequest).filter(PolicyPullRequest.id == pr_id).first()
    
    if not pr:
        raise HTTPException(status_code=404, detail="Policy PR not found")
    
    return {
        "id": pr.id,
        "gap_id": pr.gap_analysis_id,
        "status": pr.status,
        "gap_description": pr.gap_description,
        "original_policy_text": pr.original_policy_text,
        "proposed_amendment": pr.proposed_amendment,
        "regulatory_citation": pr.regulatory_citation,
        "before_text": pr.before_text,
        "after_text": pr.after_text,
        "diff_summary": pr.diff_summary,
        "suggested_owner": pr.suggested_owner,
        "risk_level": pr.risk_level,
        "confidence_score": pr.confidence_score,
        "created_at": pr.created_at.isoformat() if pr.created_at else None,
        "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
        "review_actions": [
            {
                "id": action.id,
                "reviewer": action.reviewer_name,
                "action": action.action,
                "comments": action.comments,
                "created_at": action.created_at.isoformat() if action.created_at else None
            }
            for action in pr.review_actions
        ]
    }


# ============================================================================
# Policy Review Endpoints (FR-6)
# ============================================================================

@app.post("/policy-prs/{pr_id}/review")
async def review_policy_pr(
    pr_id: int,
    reviewer_name: str,
    action: str,
    comments: str = "",
    db: Session = Depends(get_db)
):
    """
    Record human review action on a policy PR.
    
    FR-6 Implementation: Human-in-the-loop governance
    
    Actions: approve, reject, modify, escalate, request_info
    """
    logger.info(f"Recording review for PR {pr_id}: {action}")
    
    # Load PR
    pr = db.query(PolicyPullRequest).filter(PolicyPullRequest.id == pr_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Policy PR not found")
    
    # Validate action
    valid_actions = ["approve", "reject", "modify", "escalate", "request_info"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")
    
    try:
        # Create review action
        review = PolicyReviewAction(
            policy_pr_id=pr_id,
            reviewer_name=reviewer_name,
            action=ReviewAction(action),
            comments=comments
        )
        
        # Update PR status based on action
        if action == "approve":
            pr.status = "approved"
        elif action == "reject":
            pr.status = "rejected"
        elif action == "modify":
            pr.status = "modified"
        elif action == "escalate":
            pr.status = "escalated"
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        logger.info(f"✓ Recorded review {review.id} for PR {pr_id}")
        
        return {
            "success": True,
            "review_id": review.id,
            "pr_id": pr_id,
            "action": action,
            "new_status": pr.status,
            "message": "Review recorded successfully"
        }
    
    except Exception as e:
        logger.error(f"Error recording review: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")


@app.get("/policy-prs/{pr_id}/review-history")
async def get_review_history(pr_id: int, db: Session = Depends(get_db)):
    """Get complete review history for a PR."""
    pr = db.query(PolicyPullRequest).filter(PolicyPullRequest.id == pr_id).first()
    
    if not pr:
        raise HTTPException(status_code=404, detail="Policy PR not found")
    
    return {
        "pr_id": pr_id,
        "current_status": pr.status,
        "total_reviews": len(pr.review_actions),
        "review_history": [
            {
                "id": action.id,
                "reviewer": action.reviewer_name,
                "action": action.action.value,
                "comments": action.comments,
                "timestamp": action.created_at.isoformat() if action.created_at else None
            }
            for action in sorted(pr.review_actions, key=lambda x: x.created_at or datetime.min)
        ]
    }


# ============================================================================
# Policy Mapping Endpoint (FR-3)
# ============================================================================

@app.post("/obligations/{obligation_id}/map-policies")
async def map_obligation_to_policies(
    obligation_id: int,
    policies: list = None,
    db: Session = Depends(get_db)
):
    """
    Map an obligation to relevant policy sections.
    
    FR-3 Implementation: Link regulatory obligations to internal policies
    """
    logger.info(f"Mapping obligation {obligation_id} to policies")
    
    # Load obligation
    obligation = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obligation:
        raise HTTPException(status_code=404, detail="Obligation not found")
    
    try:
        # Use default policies if not provided
        if not policies:
            policies = [
                {"name": "Security Policy", "text": "Organization security measures and controls"},
                {"name": "Data Protection Policy", "text": "Personal data handling and protection"},
                {"name": "Audit Policy", "text": "Regular audits and compliance reviews"},
                {"name": "Operations Policy", "text": "Operational procedures and controls"},
                {"name": "Reporting Policy", "text": "Regulatory reporting requirements"}
            ]
        
        # Map obligation to policies
        mapper = get_policy_mapper()
        mapping_result = mapper.map_obligation_to_policies(
            obligation.obligation_text,
            obligation.source_citation or "Unknown",
            policies,
            confidence_threshold=0.5
        )
        
        logger.info(f"✓ Mapped obligation to {mapping_result['matching_policies']} policies")
        
        return mapping_result
    
    except Exception as e:
        logger.error(f"Error mapping policies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Mapping failed: {str(e)}")


# ============================================================================
# Gap Analysis AI Endpoints (FR-4 Enhancement)
# ============================================================================

@app.post("/gaps/{gap_id}/analyze-with-ai")
async def analyze_gap_with_ai(
    gap_id: int,
    db: Session = Depends(get_db)
):
    """
    Perform AI-powered gap analysis with risk scoring.
    
    FR-4 Implementation: Enhanced gap analysis with AI insights
    """
    logger.info(f"Performing AI analysis for gap {gap_id}")
    
    # Load gap and obligation
    gap = db.query(GapAnalysis).filter(GapAnalysis.id == gap_id).first()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")
    
    obligation = gap.obligation
    if not obligation:
        raise HTTPException(status_code=404, detail="Associated obligation not found")
    
    try:
        # Perform AI gap analysis
        ai_service = get_gap_analysis_ai()
        analysis = ai_service.analyze_gap_with_ai(
            obligation_text=obligation.obligation_text,
            obligation_category=obligation.category,
            obligation_priority=obligation.priority,
            current_coverage=gap.coverage_score,
            responsible_team=obligation.responsible_team,
            evidence_required=obligation.evidence_required
        )
        
        logger.info(f"✓ AI gap analysis complete for gap {gap_id}")
        
        return {
            "success": True,
            "gap_id": gap_id,
            "obligation_id": obligation.id,
            "ai_analysis": analysis,
            "message": "AI-powered gap analysis completed"
        }
    
    except Exception as e:
        logger.error(f"Error analyzing gap: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/documents/{document_id}/deep-gap-analysis")
async def deep_gap_analysis(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Perform comprehensive AI-powered gap analysis for all obligations in document.
    
    FR-4 Implementation: Deep gap analysis with risk scoring and recommendations
    """
    logger.info(f"Starting deep gap analysis for document {document_id}")
    
    # Load document
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        ai_service = get_gap_analysis_ai()
        
        gap_analyses = []
        risk_summary = {
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "average_risk_score": 0.0,
            "highest_risk_obligation": None
        }
        
        total_risk = 0.0
        highest_risk = 0.0
        highest_risk_ob = None
        
        # Analyze each obligation
        for obligation in doc.obligations:
            gap = obligation.gap_analysis
            if not gap:
                continue
            
            # Perform AI analysis
            analysis = ai_service.analyze_gap_with_ai(
                obligation_text=obligation.obligation_text,
                obligation_category=obligation.category,
                obligation_priority=obligation.priority,
                current_coverage=gap.coverage_score,
                responsible_team=obligation.responsible_team,
                evidence_required=obligation.evidence_required
            )
            
            risk_score = analysis["gap_analysis"]["risk_score"]
            severity = analysis["gap_analysis"]["severity"]
            
            total_risk += risk_score
            
            # Track highest risk
            if risk_score > highest_risk:
                highest_risk = risk_score
                highest_risk_ob = obligation.obligation_id
            
            # Count severity levels
            if severity == "critical":
                risk_summary["critical_count"] += 1
            elif severity == "high":
                risk_summary["high_count"] += 1
            elif severity == "medium":
                risk_summary["medium_count"] += 1
            else:
                risk_summary["low_count"] += 1
            
            gap_analyses.append({
                "obligation_id": obligation.obligation_id,
                "obligation_text": obligation.obligation_text[:100],
                "analysis": analysis
            })
        
        # Calculate averages
        if gap_analyses:
            risk_summary["average_risk_score"] = total_risk / len(gap_analyses)
            risk_summary["highest_risk_obligation"] = highest_risk_ob
        
        logger.info(f"✓ Deep gap analysis complete: {len(gap_analyses)} gaps analyzed")
        
        return {
            "success": True,
            "document_id": document_id,
            "total_gaps_analyzed": len(gap_analyses),
            "risk_summary": risk_summary,
            "gap_analyses": gap_analyses,
            "overall_risk_level": _calculate_overall_risk(risk_summary),
            "message": "Deep gap analysis completed with AI insights"
        }
    
    except Exception as e:
        logger.error(f"Error in deep gap analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def _calculate_overall_risk(risk_summary: dict) -> str:
    """Determine overall risk level from risk summary."""
    if risk_summary["critical_count"] > 0:
        return "critical"
    elif risk_summary["high_count"] > 2:
        return "high"
    elif risk_summary["average_risk_score"] > 0.6:
        return "high"
    elif risk_summary["average_risk_score"] > 0.4:
        return "medium"
    else:
        return "low"


# ============================================================================
# Audit Trail Endpoint (FR-7)
# ============================================================================

@app.get("/audit-trail/{document_id}")
async def get_audit_trail(document_id: int, db: Session = Depends(get_db)):
    """
    Get complete audit trail for a document.
    
    FR-7 Implementation: Full traceability from regulation to decision
    Shows: source → obligation → mapping → gap → amendment → review
    """
    logger.info(f"Retrieving audit trail for document {document_id}")
    
    # Load document
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Build comprehensive audit trail
        audit_trail = {
            "document_id": document_id,
            "document_name": doc.filename,
            "document_uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
            "obligations": []
        }
        
        for obligation in doc.obligations:
            obligation_record = {
                "obligation_id": obligation.obligation_id,
                "obligation_text": obligation.obligation_text,
                "category": obligation.category,
                "priority": obligation.priority,
                "responsible_team": obligation.responsible_team,
                "source_citation": obligation.source_citation,
                "confidence_score": obligation.confidence_score,
                "extracted_at": obligation.created_at.isoformat() if obligation.created_at else None,
                "gap_analysis": None,
                "policy_pr": None,
                "review_history": []
            }
            
            # Add gap analysis if exists
            if obligation.gap_analysis:
                gap = obligation.gap_analysis
                obligation_record["gap_analysis"] = {
                    "status": gap.status,
                    "coverage_score": gap.coverage_score,
                    "gap_summary": gap.gap_summary,
                    "recommended_action": gap.recommended_action,
                    "created_at": gap.created_at.isoformat() if gap.created_at else None
                }
                
                # Add policy PR if exists
                pr = db.query(PolicyPullRequest).filter(
                    PolicyPullRequest.gap_analysis_id == gap.id
                ).first()
                
                if pr:
                    obligation_record["policy_pr"] = {
                        "id": pr.id,
                        "status": pr.status,
                        "proposed_amendment": pr.proposed_amendment[:200],
                        "risk_level": pr.risk_level,
                        "created_at": pr.created_at.isoformat() if pr.created_at else None
                    }
                    
                    # Add review history
                    for review in pr.review_actions:
                        obligation_record["review_history"].append({
                            "reviewer": review.reviewer_name,
                            "action": review.action.value,
                            "comments": review.comments,
                            "timestamp": review.created_at.isoformat() if review.created_at else None
                        })
            
            audit_trail["obligations"].append(obligation_record)
        
        logger.info(f"✓ Generated audit trail with {len(audit_trail['obligations'])} obligations")
        
        return audit_trail
    
    except Exception as e:
        logger.error(f"Error generating audit trail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audit trail generation failed: {str(e)}")


# ============================================================================
# Export Endpoints (FR-8)
# ============================================================================

def _build_audit_export_payload(document_id: int, db: Session):
    """Synchronous audit payload builder for export endpoints."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    audit_trail = {
        "document_id": document_id,
        "document_name": doc.filename,
        "document_uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
        "obligations": []
    }

    for obligation in doc.obligations:
        obligation_record = {
            "obligation_id": obligation.obligation_id,
            "obligation_text": obligation.obligation_text,
            "category": obligation.category.value if hasattr(obligation.category, "value") else obligation.category,
            "priority": obligation.priority.value if hasattr(obligation.priority, "value") else obligation.priority,
            "responsible_team": obligation.responsible_team,
            "source_citation": obligation.source_citation,
            "confidence_score": obligation.confidence_score,
            "extracted_at": obligation.created_at.isoformat() if obligation.created_at else None,
            "gap_analysis": None,
            "policy_pr": None,
            "review_history": []
        }

        if obligation.gap_analysis:
            gap = obligation.gap_analysis
            obligation_record["gap_analysis"] = {
                "status": gap.status.value if hasattr(gap.status, "value") else gap.status,
                "coverage_score": gap.coverage_score,
                "gap_summary": gap.gap_summary,
                "recommended_action": gap.recommended_action,
                "created_at": gap.created_at.isoformat() if gap.created_at else None
            }

            pr = db.query(PolicyPullRequest).filter(
                PolicyPullRequest.gap_analysis_id == gap.id
            ).first()

            if pr:
                obligation_record["policy_pr"] = {
                    "id": pr.id,
                    "status": pr.status.value if hasattr(pr.status, "value") else pr.status,
                    "proposed_amendment": pr.proposed_amendment[:200],
                    "risk_level": pr.risk_level,
                    "created_at": pr.created_at.isoformat() if pr.created_at else None
                }

                for review in pr.review_actions:
                    obligation_record["review_history"].append({
                        "reviewer": review.reviewer_name,
                        "action": review.action.value,
                        "comments": review.comments,
                        "timestamp": review.created_at.isoformat() if review.created_at else None
                    })

        audit_trail["obligations"].append(obligation_record)

    return audit_trail

def _build_document_export_package(document_id: int, db: Session):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    gaps = db.query(GapAnalysis).join(Obligation).filter(
        Obligation.document_id == document_id
    ).all()

    policy_prs = db.query(PolicyPullRequest).join(GapAnalysis).join(Obligation).filter(
        Obligation.document_id == document_id
    ).all()

    review_actions = []
    for pr in policy_prs:
        for action in pr.review_actions:
            review_actions.append({
                "id": action.id,
                "policy_pr_id": pr.id,
                "reviewer": action.reviewer_name,
                "action": action.action.value,
                "comments": action.comments,
                "timestamp": action.created_at.isoformat() if action.created_at else None,
            })

    return {
        "document": {
            "id": doc.id,
            "filename": doc.filename,
            "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
            "text_length": doc.text_length
        },
        "obligations": [
            {
                "id": ob.id,
                "obligation_id": ob.obligation_id,
                "obligation_text": ob.obligation_text,
                "category": ob.category,
                "priority": ob.priority,
                "responsible_team": ob.responsible_team,
                "confidence_score": ob.confidence_score,
                "source_citation": ob.source_citation,
                "evidence_required": ob.evidence_required,
                "deadline_or_frequency": ob.deadline_or_frequency
            }
            for ob in doc.obligations
        ],
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
        ],
        "policy_pull_requests": [
            {
                "id": pr.id,
                "gap_id": pr.gap_analysis_id,
                "status": pr.status,
                "gap_description": pr.gap_description,
                "proposed_amendment": pr.proposed_amendment,
                "regulatory_citation": pr.regulatory_citation,
                "suggested_owner": pr.suggested_owner,
                "risk_level": pr.risk_level,
                "confidence_score": pr.confidence_score,
                "before_text": pr.before_text,
                "after_text": pr.after_text,
                "diff_summary": pr.diff_summary,
                "created_at": pr.created_at.isoformat() if pr.created_at else None
            }
            for pr in policy_prs
        ],
        "review_actions": review_actions,
        "audit_trail": _build_audit_export_payload(document_id, db),
        "export_timestamp": datetime.utcnow().isoformat()
    }


def _build_global_export_package(db: Session):
    documents = db.query(Document).all()
    obligations = db.query(Obligation).all()
    gaps = db.query(GapAnalysis).all()
    policy_prs = db.query(PolicyPullRequest).all()
    review_actions = db.query(PolicyReviewAction).all()

    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                "text_length": doc.text_length,
                "obligations_count": len(doc.obligations)
            }
            for doc in documents
        ],
        "obligations": [
            {
                "id": ob.id,
                "obligation_id": ob.obligation_id,
                "document_id": ob.document_id,
                "obligation_text": ob.obligation_text,
                "category": ob.category,
                "priority": ob.priority,
                "responsible_team": ob.responsible_team,
                "confidence_score": ob.confidence_score,
                "source_citation": ob.source_citation,
            }
            for ob in obligations
        ],
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
        ],
        "policy_pull_requests": [
            {
                "id": pr.id,
                "gap_id": pr.gap_analysis_id,
                "status": pr.status,
                "gap_description": pr.gap_description,
                "proposed_amendment": pr.proposed_amendment,
                "regulatory_citation": pr.regulatory_citation,
                "suggested_owner": pr.suggested_owner,
                "risk_level": pr.risk_level,
                "confidence_score": pr.confidence_score,
                "created_at": pr.created_at.isoformat() if pr.created_at else None
            }
            for pr in policy_prs
        ],
        "review_actions": [
            {
                "id": action.id,
                "policy_pr_id": action.policy_pr_id,
                "reviewer": action.reviewer_name,
                "action": action.action.value,
                "comments": action.comments,
                "timestamp": action.created_at.isoformat() if action.created_at else None
            }
            for action in review_actions
        ],
        "export_timestamp": datetime.utcnow().isoformat()
    }

@app.get("/documents/{document_id}/export/json")
async def export_json(document_id: int, db: Session = Depends(get_db)):
    """
    Export compliance package as JSON.
    
    FR-8 Implementation: Complete export for audit/review
    """
    logger.info(f"Exporting document {document_id} as JSON")
    
    try:
        return _build_document_export_package(document_id, db)
    
    except Exception as e:
        logger.error(f"Error exporting JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.get("/export/compliance-package")
async def export_compliance_package(db: Session = Depends(get_db)):
    """
    Export complete compliance package as CSV.
    
    FR-8 Implementation: Download all compliance data for external reporting/audit
    Includes: documents, obligations, gaps, compliance scores
    """
    logger.info("Exporting compliance package as CSV")
    
    try:
        import csv
        from io import StringIO
        from fastapi.responses import StreamingResponse
        
        # Get all data
        package = _build_global_export_package(db)
        documents = db.query(Document).all()
        obligations = db.query(Obligation).all()
        gaps = db.query(GapAnalysis).all()
        policy_prs = package["policy_pull_requests"]
        review_actions = package["review_actions"]
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Report Generated",
            datetime.utcnow().isoformat()
        ])
        writer.writerow([])  # Blank line
        
        # Section 1: Documents Summary
        writer.writerow(["DOCUMENTS SUMMARY"])
        writer.writerow(["Document ID", "Filename", "Uploaded At", "Text Length (bytes)", "Obligations Count"])
        
        for doc in documents:
            writer.writerow([
                doc.id,
                doc.filename,
                doc.uploaded_at.isoformat() if doc.uploaded_at else "",
                doc.text_length,
                len(doc.obligations)
            ])
        
        writer.writerow([])  # Blank line
        
        # Section 2: Obligations
        writer.writerow(["OBLIGATIONS"])
        writer.writerow([
            "Obligation ID", 
            "Category", 
            "Priority", 
            "Obligation Text", 
            "Responsible Team",
            "Confidence Score",
            "Source Citation",
            "Deadline/Frequency"
        ])
        
        for obl in obligations:
            writer.writerow([
                obl.obligation_id,
                obl.category,
                obl.priority,
                obl.obligation_text[:100] + "..." if len(obl.obligation_text) > 100 else obl.obligation_text,
                obl.responsible_team,
                f"{obl.confidence_score:.2f}" if obl.confidence_score else "",
                obl.source_citation if obl.source_citation else "",
                obl.deadline_or_frequency if obl.deadline_or_frequency else ""
            ])
        
        writer.writerow([])  # Blank line
        
        # Section 3: Gap Analysis
        writer.writerow(["GAP ANALYSIS"])
        writer.writerow([
            "Obligation ID",
            "Status",
            "Coverage Score (%)",
            "Gap Summary",
            "Recommended Action"
        ])
        
        for gap in gaps:
            writer.writerow([
                gap.obligation_id,
                gap.status,
                f"{gap.coverage_score:.1f}" if gap.coverage_score else "0",
                gap.gap_summary[:100] + "..." if gap.gap_summary and len(gap.gap_summary) > 100 else (gap.gap_summary or ""),
                gap.recommended_action[:100] + "..." if gap.recommended_action and len(gap.recommended_action) > 100 else (gap.recommended_action or "")
            ])
        
        writer.writerow([])  # Blank line
        
        # Section 4: Compliance Summary
        writer.writerow(["COMPLIANCE SUMMARY"])
        
        # Calculate summary stats
        total_obligations = len(obligations)
        total_gaps = len(gaps)
        avg_coverage = sum(gap.coverage_score for gap in gaps) / len(gaps) if gaps else 0
        
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Documents", len(documents)])
        writer.writerow(["Total Obligations", total_obligations])
        writer.writerow(["Total Gaps", total_gaps])
        writer.writerow(["Average Coverage Score", f"{avg_coverage:.1f}%"])
        
        # Priority breakdown
        high_count = len([o for o in obligations if o.priority == "high"])
        medium_count = len([o for o in obligations if o.priority == "medium"])
        low_count = len([o for o in obligations if o.priority == "low"])
        
        writer.writerow([])
        writer.writerow(["PRIORITY BREAKDOWN"])
        writer.writerow(["High Priority", high_count])
        writer.writerow(["Medium Priority", medium_count])
        writer.writerow(["Low Priority", low_count])

        writer.writerow([])
        writer.writerow(["POLICY PULL REQUESTS"])
        writer.writerow([
            "PR ID",
            "Gap ID",
            "Status",
            "Risk Level",
            "Suggested Owner",
            "Confidence Score",
            "Regulatory Citation"
        ])
        for pr in policy_prs:
            writer.writerow([
                pr["id"],
                pr["gap_id"],
                pr["status"],
                pr["risk_level"],
                pr["suggested_owner"],
                pr["confidence_score"],
                pr["regulatory_citation"],
            ])

        writer.writerow([])
        writer.writerow(["REVIEW ACTIONS"])
        writer.writerow([
            "Review ID",
            "Policy PR ID",
            "Reviewer",
            "Action",
            "Comments",
            "Timestamp"
        ])
        for action in review_actions:
            writer.writerow([
                action["id"],
                action["policy_pr_id"],
                action["reviewer"],
                action["action"],
                action["comments"],
                action["timestamp"],
            ])

        # Get CSV content
        csv_content = output.getvalue()
        output.close()
        
        logger.info(f"✓ Generated compliance package CSV ({len(csv_content)} bytes)")
        
        # Return as downloadable CSV
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=compliance-package.csv"}
        )
    
    except Exception as e:
        logger.error(f"Error exporting compliance package: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.get("/export/compliance-package/json")
async def export_compliance_package_json(db: Session = Depends(get_db)):
    """Export the full compliance package as structured JSON."""
    logger.info("Exporting compliance package as JSON")
    try:
        return _build_global_export_package(db)
    except Exception as e:
        logger.error(f"Error exporting compliance package JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
