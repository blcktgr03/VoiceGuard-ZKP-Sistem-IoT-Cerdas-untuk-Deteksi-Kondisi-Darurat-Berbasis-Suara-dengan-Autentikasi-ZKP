# Index Task Completion Map — Lab 12

**Nama:** Muhamad Umar Nugroho — **NPM:** 2322101943 — **Kelas:** III RPKK

Dokumen ini memetakan setiap task utama pada `Paparan/lab12-capstone-project/index.qmd` ke jawaban dan bukti VoiceGuard-ZKP.

| Task | Requirement | Answer/evidence | Status |
|---|---|---|---|
| 1.1 | Problem definition, context, data, metrics, constraints, deliverables | `PROJECT_PROPOSAL_TEMPLATE.md` sections 1–7 | Complete |
| 1.2 | Risk assessment | Proposal section 5 + Worksheet 2 | Complete |
| 2.1 | Load dataset | `EDA_REPORT.md` sections 2–3 | Complete |
| 2.2 | Comprehensive EDA | `EDA_REPORT.md` sections 3–12 | Complete; metadata-limited analyses disclosed |
| 2.3 | Reproducible preprocessing/split | Technical Report 4.3–4.4 + Experiment Report 2 | Complete for final CSV→split; raw lineage partial |
| 3.1 | Baseline model | Experiment Report 3 | Complete |
| 3.2 | Systematic model comparison | Experiment Report 3 and 6 | Complete: 4 baselines + IndoBERT |
| 3.3 | Hyperparameter optimization | Experiment Report 4 | Partial: one-dimensional LinearSVC tuning; IndoBERT not tuned |
| 3.4 | Robust validation/CV | Experiment Report 5 | Complete for baseline; IndoBERT CV missing |
| 4.1 | Save model/preprocessor/metadata | Model Card + existing model/tokenizer/metadata artifacts | Complete |
| 4.2 | Build REST API | Deployment and Testing sections 1–7 | Complete for project-specific API |
| 4.3 | Dockerfile | Deployment and Testing section 12 | Not complete; no Docker files found |
| 4.4 | Model card/monitoring | `MODEL_CARD_TEMPLATE.md` sections 7–10 | Complete as documentation |
| 5.1 | Technical report | `TECHNICAL_REPORT.md` | Complete |
| 5.2 | Final presentation | `PRESENTATION_GUIDE.md` + source PDF | Content complete; rehearsal/delivery pending |

## Final Checklist Mapping

### Code & Implementation

- Notebook: available at `dataset/train_bert_final_dataset.ipynb`.
- Tests: 34 passed.
- Error handling/comments: present in backend.
- Credentials: firmware remediation required.
- Requirements: available, partially pinned.

### Data & Analysis

- Dataset, EDA, split, quality, and errors documented.
- Raw-source reproducibility and provenance remain partial.

### Model Development

- Baseline and 3+ models: complete.
- Tuning and CV: complete for LinearSVC, incomplete for IndoBERT.
- Best model: IndoBERT selected with test evidence.

### Deployment

- Model/API/dashboard/health: available.
- Docker: missing.
- Security production controls: pending.

### Documentation

- Proposal, README, model card, technical report, EDA, experiments: complete.

### Presentation

- Slide content, script, Q&A, demo flow: complete.
- Practice and final delivery evidence: pending.

### Git and Quality

- Repository structured, README and `.gitignore` available.
- Worktree is not clean and contains large local artifacts; cleanup/versioning strategy required.

## Overall Status

The academic prototype and its documentation are substantially complete. Production-readiness tasks are explicitly open and should not be checked off until verified.

