# RegLoop AI

RegLoop AI is a closed-loop regulatory execution prototype for the challenge workflow:
'updated by elena'
`Regulation -> Obligation Extraction -> Gap Analysis -> Policy Pull Request -> Human Review -> Audit Trail -> Export`

## What It Does

The app helps a compliance team move from a new regulation to structured obligations, gaps, reviewable policy recommendations, human approvals, and exportable audit evidence...

The verified workflow supports:

- a unified review workspace for:
  - one regulation PDF
  - one to three policy PDFs
  - one responsibility matrix CSV
- obligation extraction from the uploaded regulation
- automatic gap creation after analysis
- policy pull request generation from gaps
- human review actions:
  - approve
  - reject
  - modify
  - escalate
- document-level audit traceability
- export of the compliance package in JSON and CSV

## Verified Challenge Data

The challenge sample bundle is supported directly:

- [sample-inputs](c:/Users/Administrator/Documents/Challenge/sample-inputs)
- DORA regulation PDF
- three policy PDFs
- responsibility matrix CSV

The app also supports the cleaned demo data stored in the backend upload folder:

- [backend/uploads](c:/Users/Administrator/Documents/Challenge/backend/uploads)

## Stack

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- SQLAlchemy
- SQLite

### AI Layer
- Google Gemini with rule-based fallback behavior in parts of the flow

## Verified Status

Validated locally on June 11, 2026:

- `python -m py_compile backend/main.py`
- `npm run lint`
- `npx tsc --noEmit`
- `npm run build`

Validated live flow:

1. Upload regulation, policy files, and responsibility matrix
2. Run analysis and create gaps
3. Create policy PRs
4. Approve a policy PR
5. View audit trail
6. Export JSON
7. Export CSV

## Quick Start

### Backend

```bash
cd backend
python main.py
```

Backend runs at:

- `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

### Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at:

- `http://localhost:3000`

## Main Pages

- `/` Dashboard
- `/documents` Review workspace
- `/obligations` Extracted obligations
- `/compliance` Gap and coverage analysis
- `/policy-review` Human review workflow
- `/audit` Audit trail

## Challenge Workflow Mapping

### FR-1 Upload Workspace

The Documents page lets the user manage the working set:

- regulation upload
- policy uploads
- responsibility matrix upload
- replace/remove documents
- gate analysis until required inputs exist

### FR-2 Obligation Extraction

The backend stores obligations with:

- text
- category
- priority
- confidence score
- source citation

### FR-3 Policy Mapping

Policy files are uploaded and used in the compliance and review flow.
The prototype demonstrates policy mapping through the downstream gap and PR workflow.

### FR-4 Gap Analysis

Analysis creates gap records automatically.
The compliance page shows:

- gap counts
- coverage score
- risk level
- recommendations

### FR-5 Policy Pull Request Generation

Each policy PR includes:

- gap description
- proposed amendment
- risk level
- confidence score
- suggested owner
- before/after comparison fields

### FR-6 Human Review Workflow

The Policy Review page supports:

- approve
- reject
- modify
- escalate

Review actions are persisted in the database.

### FR-7 Audit Trail

The Audit Trail page shows traceability across:

- upload
- extraction
- gap assessment
- PR generation
- review action

### FR-8 Export

Exports include:

- obligations
- gaps
- policy pull requests
- review actions
- audit payloads

Formats:

- JSON
- CSV

## Important API Endpoints

### Upload and Documents

- `POST /upload`
- `POST /upload/responsibility-matrix`
- `GET /documents`
- `GET /documents/{document_id}`
- `DELETE /documents/{document_id}`

### Analysis

- `POST /documents/{document_id}/analyze-and-gaps`
- `GET /obligations`
- `GET /gap-analysis`
- `GET /compliance-summary`

### Policy Review

- `POST /gaps/{gap_id}/create-pr`
- `GET /policy-prs`
- `GET /policy-prs/{pr_id}`
- `POST /policy-prs/{pr_id}/review`
- `GET /policy-prs/{pr_id}/review-history`

### Audit and Export

- `GET /audit-trail/{document_id}`
- `GET /documents/{document_id}/export/json`
- `GET /export/compliance-package`
- `GET /export/compliance-package/json`

## Demo Files

Use these docs for the final recording and submission:

- [SETUP_INSTRUCTIONS.md](c:/Users/Administrator/Documents/Challenge/SETUP_INSTRUCTIONS.md)
- [FINAL_DEMO_RUNBOOK.md](c:/Users/Administrator/Documents/Challenge/FINAL_DEMO_RUNBOOK.md)
- [DEMO_VIDEO_GUIDE.md](c:/Users/Administrator/Documents/Challenge/DEMO_VIDEO_GUIDE.md)
- [FINAL_SPEAKER_SCRIPT.md](c:/Users/Administrator/Documents/Challenge/FINAL_SPEAKER_SCRIPT.md)
- [FINAL_STATUS_REPORT.md](c:/Users/Administrator/Documents/Challenge/FINAL_STATUS_REPORT.md)
- [FINAL_SUBMISSION_PACKAGE.md](c:/Users/Administrator/Documents/Challenge/FINAL_SUBMISSION_PACKAGE.md)
- [SUBMISSION_CHECKLIST.md](c:/Users/Administrator/Documents/Challenge/SUBMISSION_CHECKLIST.md)
- [ARCHITECTURE_DIAGRAM.svg](c:/Users/Administrator/Documents/Challenge/ARCHITECTURE_DIAGRAM.svg)

## Submission Contents

Include:

- `backend/`
- `frontend/`
- `README.md`
- `SETUP_INSTRUCTIONS.md`
- `ARCHITECTURE.md`
- `ARCHITECTURE_DIAGRAM.svg`
- `SAMPLE_DATA_GUIDE.md`
- `DEMO_VIDEO_GUIDE.md`
- `FINAL_DEMO_RUNBOOK.md`
- `FINAL_SPEAKER_SCRIPT.md`
- `FINAL_STATUS_REPORT.md`
- `FINAL_SUBMISSION_PACKAGE.md`
- `SUBMISSION_CHECKLIST.md`

Do not include:

- `backend/.env`
- `backend/venv`
- `frontend/.next`
- `frontend/node_modules`
- reset backups
- machine-specific caches

\
## Notes

- The repository contains verified sample data and a live demo path.
- The cleanest presentation is to use the populated sample dataset and walk reviewers through the workflow quickly.
