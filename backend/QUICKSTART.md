# Quick Start Guide - RegLoop AI Database

## Setup (Already Completed ✅)

Your database layer is fully installed and configured. All dependencies are installed in your Python environment.

## Running the Application

```bash
cd backend
python -m uvicorn main:app --reload
```

Visit: `http://localhost:8000/docs` for interactive API documentation

## Test the API

### 1. Upload a PDF Document

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@path/to/your/document.pdf"
```

Response:
```json
{
  "success": true,
  "document_id": 1,
  "filename": "document.pdf",
  "text_length": 5420,
  "preview": "First 500 chars of extracted text..."
}
```

### 2. View All Documents

```bash
curl "http://localhost:8000/documents"
```

### 3. Get Document Details

```bash
curl "http://localhost:8000/documents/1"
```

### 4. Create Obligations (After Claude Analysis)

```bash
curl -X POST "http://localhost:8000/documents/1/obligations" \
  -H "Content-Type: application/json" \
  -d '{
    "obligation_id": "GDPR_001",
    "obligation_text": "Data protection by design required",
    "category": "documentation",
    "priority": "critical",
    "responsible_team": "DPO",
    "deadline_or_frequency": "Ongoing"
  }'
```

### 5. View Compliance Summary

```bash
curl "http://localhost:8000/compliance-summary"
```

## Database Files

| File | Contents |
|------|----------|
| `database/db.py` | Database connection, SessionLocal setup, init_db() |
| `database/models.py` | SQLAlchemy ORM models (Document, Obligation, GapAnalysis) |
| `database/schemas.py` | Pydantic schemas for API validation |
| `database/examples.py` | 10+ working examples of insertions and queries |
| `main.py` | FastAPI app with database integration |

## Database Tables

### documents
- id, filename, document_type, uploaded_at, text_length, raw_text
- One document → Many obligations

### obligations
- id, document_id, obligation_id, obligation_text, category, priority, responsible_team, deadline_or_frequency, risk_if_not_met, created_at
- Many obligations → One document
- One obligation → One gap_analysis

### gap_analysis
- id, obligation_id, status, coverage_score, gap_summary, recommended_action, created_at, updated_at
- One gap_analysis → One obligation

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/upload` | Upload PDF, extract text, save document |
| GET | `/documents` | List all documents |
| GET | `/documents/{id}` | Get document with obligations & gaps |
| GET | `/obligations` | Query obligations (filter by priority/category) |
| POST | `/documents/{id}/obligations` | Create obligation from Claude analysis |
| GET | `/gap-analysis` | Query gap analyses (filter by status) |
| GET | `/compliance-summary` | Get compliance metrics by category |

## Integration with Claude

When you integrate Claude:

```python
# After Claude analyzes extracted text
obligations_from_claude = [...]  # Parsed from Claude response

for ob_data in obligations_from_claude:
    response = requests.post(
        f"http://localhost:8000/documents/{doc_id}/obligations",
        json=ob_data
    )
```

## Data Flow

```
1. PDF Upload → /upload endpoint
   ↓
2. Text Extraction (pdfplumber)
   ↓
3. Save Document to DB
   ↓
4. Send to Claude for Analysis
   ↓
5. Parse Claude Response
   ↓
6. Create Obligations via /obligations endpoint
   ↓
7. Gap Analysis populated
   ↓
8. Query via compliance-summary
```

## Example: Complete Workflow

```python
import requests

# 1. Upload document
with open("regulation.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": f}
    )
    doc_id = response.json()["document_id"]

# 2. Get extracted text
doc = requests.get(f"http://localhost:8000/documents/{doc_id}").json()
text = doc["raw_text"]

# 3. Send to Claude (your code)
# obligations = claude_analyze(text)

# 4. Create obligations
for ob in obligations:
    requests.post(
        f"http://localhost:8000/documents/{doc_id}/obligations",
        json=ob
    )

# 5. View summary
summary = requests.get("http://localhost:8000/compliance-summary").json()
print(summary)
```

## Testing Queries Locally

```python
from database.db import SessionLocal
from database.models import Document, Obligation

db = SessionLocal()

# Get all documents
docs = db.query(Document).all()
print(f"Total documents: {len(docs)}")

# Get critical obligations
from database.models import PriorityLevel
critical = db.query(Obligation).filter(
    Obligation.priority == PriorityLevel.CRITICAL
).all()

db.close()
```

## Database File Location

The SQLite database file `regloop.db` is created in your backend directory:

```
backend/regloop.db
```

You can inspect it with any SQLite viewer or use:

```bash
sqlite3 backend/regloop.db
.tables  # View all tables
.schema  # View table structure
SELECT * FROM documents;
```

## Common Tasks

### Check Database Schema
```bash
sqlite3 backend/regloop.db ".schema"
```

### Clear All Data (Dev Only)
```python
from database.db import drop_db, init_db
drop_db()
init_db()
```

### View SQL Queries
Set environment variable before running:
```bash
export SQL_ECHO=true
python -m uvicorn main:app --reload
```

## Next Steps

1. ✅ Database layer ready
2. 📝 Integrate Claude API for obligation analysis
3. 🔄 Implement gap analysis creation
4. 📊 Build frontend dashboards
5. 🚀 Deploy to production

All foundation code is production-ready!
