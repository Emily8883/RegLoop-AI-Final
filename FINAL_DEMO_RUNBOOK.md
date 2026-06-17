# RegLoop AI Final Demo Runbook

## Goal

Use this runbook for the final submission video or a live reviewer demo.

The verified challenge data set is:

- `DORA_ICT_Risk_Update_2026.pdf`
- `ICT_Risk_Policy.pdf`
- `Vendor_Risk_Policy.pdf`
- `Incident_Response_Policy.pdf`
- `responsibility_matrix.csv`

## Known Good State

The following was verified locally:

- 12 obligations extracted from the DORA regulation
- 12 gaps created
- policy PR creation works
- PR approval works
- audit trail loads
- export works

## Before You Record

1. Start backend:

```bash
cd backend
python main.py
```

2. Start frontend:

```bash
cd frontend
npm run dev
```

3. Open:

- Frontend: `http://localhost:3000`
- Backend docs: `http://127.0.0.1:8000/docs`

## Recommended Demo Flow

1. Dashboard
2. Documents
3. Obligations
4. Compliance
5. Policy Review
6. Audit Trail
7. Export

## Short Talk Track

### Opening

"RegLoop AI turns a regulation into obligations, gaps, policy recommendations, human review actions, audit evidence, and exportable output."

### Documents

Show the 5 uploaded files and say:

"This workspace accepts one regulation, one to three policy documents, and a responsibility matrix."

### Obligations

Show extracted obligations and say:

"The app converts source text into structured obligations with confidence and citations."

### Compliance

Show the red gap rows and say:

"The compliance page creates risk-prioritized gaps and lets us generate policy PRs from them."

### Policy Review

Show the created PR and approve it.

Say:

"Policy actions stay human-reviewed. AI proposes the change, but people approve it."

### Audit Trail

Open the audit trail for the DORA regulation and show the refreshed timeline.

Say:

"The audit trail records the full compliance history for this regulation."

### Export

Download JSON or CSV.

Say:

"The full compliance package is exportable for reporting and submission use."

## What To Click

Minimal-click version:

1. Open dashboard
2. Open Documents
3. Open Obligations
4. Open Compliance
5. Create one PR
6. Open Policy Review
7. Approve it
8. Open Audit Trail
9. Refresh the audit trail
10. Export JSON or CSV

## What To Avoid

- Do not upload files slowly during the recording
- Do not show the old development data
- Do not show terminal logs
- Do not use the `__MACOSX` folder

## Final Recording Checklist

- [ ] Frontend and backend start cleanly
- [ ] Sample files visible in Documents
- [ ] Obligations extracted
- [ ] Gaps created
- [ ] PR created
- [ ] PR approved
- [ ] Audit trail shows the approval event
- [ ] Export works
