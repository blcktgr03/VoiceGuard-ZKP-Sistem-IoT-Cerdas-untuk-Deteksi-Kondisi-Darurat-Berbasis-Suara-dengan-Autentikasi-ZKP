# Rubric Self-Assessment — VoiceGuard-ZKP

**Nama:** Muhamad Umar Nugroho  
**NPM:** 2322101943  
**Kelas:** III RPKK  
**Catatan:** skor ini adalah penilaian diri berbasis bukti, bukan nilai resmi dosen.

## Score Summary

| Category | Maximum | Self-score | Main reason |
|---|---:|---:|---|
| 1. Problem Definition & Planning | 15 | 14 | Masalah/SMART/scope/risk lengkap; timeline awal tidak memiliki time log rinci |
| 2. Data & Analysis | 15 | 12 | Audit data kuat; provenance, source-level EDA, dan fairness metadata belum ada |
| 3. Model Development | 25 | 18 | 4 baseline + IndoBERT dan 5-fold CV; tuning IndoBERT belum sistematis |
| 4. Evaluation & Results | 20 | 17 | Metrik/error analysis lengkap; ROC/PR IndoBERT dan audio E2E belum ada |
| 5. Documentation & Code Quality | 15 | 12 | Dokumentasi sangat lengkap; credential firmware, dirty worktree, dan Docker gap |
| 6. Presentation | 10 | 5 | Paparan/struktur/Q&A tersedia; latihan dan final demo belum terverifikasi |
| **Total** | **100** | **78** | Functional prototype with important production evidence gaps |
| Bonus | +10 | 0 claimed | Transfer learning ada, tetapi bonus diserahkan kepada dosen |

## 1. Problem Definition & Planning — 14/15

### 1.1 Problem Statement — 5/5

Evidence:

- Problem spesifik: deteksi teks darurat dari audio device terdaftar.
- Measurable: accuracy, precision, recall, F1, confusion matrix, tests, latency target.
- Achievable: dua kelas, Indonesia, prototype lokal.
- Relevant: kanal hands-free tambahan dan lokasi event.
- Time-bound: milestone Week 13–14.
- Business/safety context serta stakeholder dijelaskan.

Referensi: [`PROJECT_PROPOSAL_TEMPLATE.md`](PROJECT_PROPOSAL_TEMPLATE.md), bagian 1–2.

### 1.2 Data Planning — 4/5

Evidence tersedia untuk sumber yang disebut paparan, ukuran final, label, kualitas, privacy/ethics, dan data dictionary. Pengurangan satu poin karena CSV final tidak memiliki provenance, speaker, noise, lisensi per sampel, atau raw-to-final lineage yang lengkap.

### 1.3 Feasibility & Timeline — 5/5

Timeline, scope in/out, 12 risiko, mitigation, resource, deliverable, dan status milestone tersedia. Estimasi jam aktual tidak dicatat, tetapi perencanaan milestone cukup rinci.

## 2. Data & Analysis — 12/15

### 2.1 Data Quality — 4/5

- Missing dan empty text = 0.
- Full duplicate = 0.
- 13 conflicting duplicate texts ditemukan dan didokumentasikan.
- Tipe, range panjang, dan label distribution diperiksa.
- Kekurangan: konflik belum diperbaiki di dataset sumber dan tiga overlap antarsplit masih ada.

### 2.2 EDA & Insights — 4/5

EDA mencakup distribusi kelas, panjang karakter/kata, kualitas, split, overlap, provenance, dan lima insight. Multivariate/source-condition analysis tidak dapat dilakukan karena metadata sumber tidak ada.

### 2.3 Feature Engineering — 4/5

Lebih dari lima fitur/guardrail domain dijelaskan; token IndoBERT, negasi, keyword, alias, repetition, STT confidence/activity, dan consecutive chunk digunakan. Dampak individual belum divalidasi melalui ablation/SHAP.

## 3. Model Development — 18/25

### 3.1 Approach & Algorithm Selection — 8/8

- Dummy baseline.
- Logistic Regression, LinearSVC, MultinomialNB.
- Fine-tuned IndoBERT.
- Trade-off accuracy/interpretability/speed/complexity dijelaskan.
- Tabel comparison dan model selection tersedia.

### 3.2 Validation Strategy — 7/9

- Split 80/10/10, stratified, seed 42.
- Test set ditahan dari tuning baseline.
- 5-fold Stratified CV dilakukan untuk LinearSVC.
- Vectorizer berada di pipeline tiap fold.
- Pengurangan: IndoBERT belum multi-fold/multi-seed; duplicate conflict menimbulkan tiga overlap teks.

### 3.3 Hyperparameter Tuning — 3/8

LinearSVC `C` diuji pada empat nilai dan improvement dikuantifikasi. IndoBERT hanya satu konfigurasi; tidak ada GridSearch/RandomSearch multi-parameter dan tidak ada threshold calibration curve. Karena itu skor sengaja rendah.

## 4. Evaluation & Results — 17/20

### 4.1 Metrics Selection — 5/5

Accuracy, per-class precision/recall/F1, macro/weighted metrics, balanced accuracy, MCC, confusion matrix, false alarm, miss rate, dan baseline comparison dilaporkan. Recall Emergency diprioritaskan berdasarkan dampak bisnis/keselamatan.

### 4.2 Results & Analysis — 6/8

- Improvement baseline dikuantifikasi.
- Confusion matrix dan error rate dianalisis.
- Smoke test menemukan redaction sensitivity.
- Keterbatasan dijelaskan secara jujur.
- Pengurangan: prediction-level failure cases, ROC/PR IndoBERT, ablation, WER, dan field audio metrics belum ada.

### 4.3 Reproducibility — 6/7

Seed/split/config/metadata/code tersedia; baseline dan tests dijalankan ulang. Pengurangan karena dependency tidak semuanya pinned, waktu training IndoBERT tidak tercatat, dan raw-source integration script tidak lengkap.

## 5. Documentation & Code Quality — 12/15

### 5.1 Code Quality — 4/5

Backend berlapis routes/services/repositories, docstring, exceptions, settings, dan tests. Kekurangan penting: firmware mengandung konfigurasi Wi-Fi hardcoded dan service memiliki `AUDIO_PLACEHOLDER` yang harus test-only.

### 5.2 Documentation — 5/5

README, proposal, model card, EDA, experiment, technical, deployment/testing, worksheet, presentation guide, dan task mapping tersedia.

### 5.3 Repository Organization — 3/5

Struktur dataset/backend/frontend/Paparan jelas dan `.gitignore` tersedia. Pengurangan karena worktree tidak bersih, model/data besar berada di workspace/repository tree, dan belum ada Docker/CI evidence.

## 6. Presentation — 5/10

### 6.1 Clarity & Storytelling — 4/5

Paparan 22 slide dan guide 16 slide memiliki alur problem→solution→data→model→result→limitation. Visual architecture/confusion matrix/dashboard tersedia.

### 6.2 Delivery & Q&A — 1/5

Q&A dan demo flow telah disiapkan, tetapi tidak ada bukti tiga kali rehearsal, delivery final, atau final real-device demo. Nilai delivery harus diberikan penguji setelah presentasi.

## Checklist Evidence Gaps

| Requirement | Status | Required action |
|---|---|---|
| Docker | Missing | Add/test Dockerfile and healthcheck |
| Full dependency pinning | Partial | Pin Transformers/Torch/Whisper |
| No hardcoded credentials | Failed | Remove and rotate firmware secrets |
| IndoBERT systematic tuning | Missing | Multi-parameter validation search |
| IndoBERT 5-fold/multi-seed | Missing | Run feasible repeated evaluation |
| Feature attribution | Missing | SHAP/Integrated Gradients with caveat |
| ROC/PR IndoBERT | Missing | Persist probabilities and plot |
| Real audio benchmark | Missing | Noise/mask/distance test matrix |
| Security attack tests | Missing | Replay/fake device/message binding tests |
| End-to-end latency | Missing | Instrument capture→notification |
| Practice/demo evidence | Missing | Rehearsal log and backup video |

## Strengths

1. End-to-end prototype menggabungkan ML, device, API, dashboard, dan authentication.
2. Evaluasi tidak hanya accuracy; false negative dan batas keamanan dibahas.
3. Dokumentasi membedakan hasil terverifikasi dari klaim/rencana.

## Areas for Improvement

1. Persempit release gate pada evidence audio lapangan dan recall.
2. Perkuat secure channel, message binding, anti-replay, dan secret handling.
3. Tingkatkan reproducibility data/model/deployment dan bersihkan repository.

## Recommended Grade Interpretation

Self-score 78 menunjukkan proyek fungsional dan cukup kuat secara akademik, tetapi masih memiliki gap penting terhadap standar production ML. Skor dapat meningkat setelah Docker, systematic tuning, audio/security/reliability benchmark, repository cleanup, dan presentation evidence diselesaikan.

