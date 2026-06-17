# Final Submission Package

This file lists what should be included in the final challenge submission.

## Include

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
- your final demo video file

## Exclude

- `backend/.env`
- `backend/venv/`
- `frontend/.next/`
- `frontend/node_modules/`
- `backend/reset_backups/`
- other temporary caches or local machine files

## Recommended Submission Layout

If the portal accepts a zip, include the repository root contents directly so the reviewer can run:

```bash
cd backend
python main.py
```

and:

```bash
cd frontend
npm run dev
```

## Before You Submit

1. Confirm the backend starts
2. Confirm the frontend starts
3. Confirm the sample-inputs flow works
4. Confirm the video file is attached
5. Confirm no secrets are included
