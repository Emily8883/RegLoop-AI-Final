# RegLoop AI Sample Data Guide

This guide explains the challenge sample bundle and how it maps to the app.

## Sample Inputs Folder

Use the files in:

- [sample-inputs](c:/Users/Administrator/Documents/Challenge/sample-inputs)

Ignore the `__MACOSX` folder inside it.

## Challenge Files

- [DORA_ICT_Risk_Update_2026.pdf](c:/Users/Administrator/Documents/Challenge/sample-inputs/DORA_ICT_Risk_Update_2026.pdf)
- [ICT_Risk_Policy.pdf](c:/Users/Administrator/Documents/Challenge/sample-inputs/ICT_Risk_Policy.pdf)
- [Vendor_Risk_Policy.pdf](c:/Users/Administrator/Documents/Challenge/sample-inputs/Vendor_Risk_Policy.pdf)
- [Incident_Response_Policy.pdf](c:/Users/Administrator/Documents/Challenge/sample-inputs/Incident_Response_Policy.pdf)
- [responsibility_matrix.csv](c:/Users/Administrator/Documents/Challenge/sample-inputs/responsibility_matrix.csv)
- [reg-loop-sample-data.md](c:/Users/Administrator/Documents/Challenge/sample-inputs/reg-loop-sample-data.md)

## What Each File Is For

### DORA regulation PDF

- Primary regulation document
- Used for obligation extraction

### ICT Risk Policy

- Internal policy file
- Used to demonstrate policy coverage against the regulation

### Vendor Risk Policy

- Internal policy file
- Used to show coverage and gap analysis

### Incident Response Policy

- Internal policy file
- Used to show incident-related obligations and gaps

### Responsibility matrix CSV

- Ownership and accountability input
- Parsed by the backend upload endpoint
- Supports both legacy and challenge CSV formats

## Verified Demo Behavior

When the sample set is uploaded, the app should show:

- uploaded files in Documents
- extracted obligations in Obligations
- gap records in Compliance
- policy PR creation in Compliance
- review actions in Policy Review
- audit traceability in Audit Trail
- JSON and CSV export

## Recommended Upload Order

1. Upload `DORA_ICT_Risk_Update_2026.pdf`
2. Upload `ICT_Risk_Policy.pdf`
3. Upload `Vendor_Risk_Policy.pdf`
4. Upload `Incident_Response_Policy.pdf`
5. Upload `responsibility_matrix.csv`
6. Run analysis on the DORA document

## Expected Outcome

With the verified flow, you should see:

- obligations extracted from the regulation
- a gap record for each obligation
- policy PRs created from gaps
- approval actions recorded in the audit trail

## Notes

- The folder may contain older development artifacts, but the sample-inputs bundle is the preferred challenge dataset.
- The challenge CSV format is now supported directly by the backend.
