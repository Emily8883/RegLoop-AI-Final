# RegLoop AI Architecture

## Overview

RegLoop AI is a single-user compliance workflow prototype built with a layered architecture:

`Frontend -> FastAPI API -> Service Layer -> SQLite`

The system is designed to support the challenge workflow from document upload through review and export.

## High-Level Flow

1. User uploads one regulation PDF, one to three policy PDFs, and a responsibility matrix CSV.
2. Backend stores the file on disk and extracts text for PDFs.
3. Analysis extracts obligations from the regulation.
4. Gap analysis generates compliance gaps.
5. Gap records can create policy pull requests.
6. A human reviewer approves, rejects, modifies, or escalates the PR.
7. The audit trail and export endpoints return the full evidence package.

## Frontend Layer

The Next.js frontend provides:

- dashboard
- documents workspace
- obligations table
- compliance analysis page
- policy review page
- audit trail page

Key frontend modules:

- `frontend/app/page.tsx`
- `frontend/app/documents/page.tsx`
- `frontend/app/obligations/page.tsx`
- `frontend/app/compliance/page.tsx`
- `frontend/app/policy-review/page.tsx`
- `frontend/app/audit/page.tsx`
- reusable UI components under `frontend/app/components`

The frontend talks to the backend through `frontend/services/api.ts`.

## Backend Layer

The FastAPI backend handles:

- document upload
- responsibility matrix upload
- document listing and deletion
- analysis and gap creation
- policy PR generation
- review actions
- audit trail generation
- export generation

Primary backend entry points:

- `backend/main.py`
- `backend/database/db.py`
- `backend/database/models.py`
- `backend/database/policy_models.py`

## Service Layer

The backend service layer contains the domain logic:

- obligation extraction
- policy mapping
- gap analysis
- compliance scoring
- policy PR generation
- Gemini wrapper logic

Representative files:

- `backend/services/enhanced_obligation_extractor.py`
- `backend/services/policy_mapper.py`
- `backend/services/gap_analysis_ai.py`
- `backend/services/compliance_scorer.py`
- `backend/services/policy_pr_generator.py`
- `backend/services/gemini_service.py`

## Data Layer

SQLite stores the application state in `backend/regloop.db`.

The main tables are:

- `documents`
- `obligations`
- `gap_analysis`
- `policy_pull_requests`
- `policy_review_actions`

Important relationships:

- one document has many obligations
- one obligation has one gap analysis record
- one gap can have one policy PR
- one PR can have many review actions

## File Storage

Uploaded source files are written to:

- `backend/uploads`

The database stores metadata and extracted text, not the full PDF binary.

## Challenge Sample Inputs

The supported sample bundle in `sample-inputs/` contains:

- `DORA_ICT_Risk_Update_2026.pdf`
- `ICT_Risk_Policy.pdf`
- `Vendor_Risk_Policy.pdf`
- `Incident_Response_Policy.pdf`
- `responsibility_matrix.csv`

The CSV parser accepts both:

- legacy `obligation_id,responsible_team,owner_email`
- challenge `Domain,Owner,Department`

## Audit Architecture

The audit trail is generated from the stored document, obligation, gap, PR, and review records.

The audit page assembles a timeline from:

- document upload timestamp
- obligation extraction timestamps
- gap analysis timestamps
- PR creation timestamps
- review action timestamps

## Export Architecture

Export endpoints produce two styles of output:

- document-specific export for one regulation
- global compliance package export across all stored records

Supported formats:

- JSON
- CSV

## Security and Reliability

The current prototype includes:

- local CORS allowlist for development
- Pydantic validation on request payloads
- SQLAlchemy relationships with cascades
- file-based uploads outside the frontend
- error handling around upload and review endpoints

This is a prototype, so production hardening would still require:

- authentication
- stronger file scanning
- object storage
- PostgreSQL
- deployment-time secrets management

## Deployment Model

Development:

- FastAPI on `127.0.0.1:8000`
- Next.js on `localhost:3000`
- SQLite file in the backend directory

## Why This Architecture Works For The Challenge

It is simple enough to demo reliably, but still shows a real end-to-end compliance workflow with:

- structured input
- AI-assisted extraction
- deterministic review controls
- traceable audit history
- exportable evidence

## Verification

The repository was validated locally with:

- Python compile check
- TypeScript type check
- lint
- frontend build

