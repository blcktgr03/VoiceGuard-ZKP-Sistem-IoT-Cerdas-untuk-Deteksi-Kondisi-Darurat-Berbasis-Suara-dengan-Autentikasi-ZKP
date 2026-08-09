# Creation Summary — Jawaban Lab 12 VoiceGuard-ZKP

**Disusun oleh:** Muhamad Umar Nugroho  
**NPM:** 2322101943  
**Kelas:** III RPKK  
**Tanggal:** 4 Agustus 2026

## Executive Summary

Paket jawaban Lab 12 telah dibuat pada folder baru di dalam `Paparan` tanpa mengubah template asli. Isi menggabungkan paparan proyek, seluruh struktur `machine_learning`, audit dataset, metadata model, eksperimen baseline yang dijalankan ulang, cross-validation, smoke test IndoBERT, dan hasil automated test.

Dokumentasi sengaja membedakan bukti terverifikasi, klaim yang hanya terdokumentasi, gap yang belum diuji, dan rencana pengembangan. Dengan pendekatan ini, hasil tidak melebih-lebihkan kemampuan prototype.

## Files Created

| File | Purpose | Status |
|---|---|---|
| `README.md` | Navigasi, overview, hasil utama, quick start | Complete |
| `PROJECT_PROPOSAL_TEMPLATE.md` | Proposal terisi lengkap | Complete |
| `MODEL_CARD_TEMPLATE.md` | Model card terisi lengkap | Complete |
| `WORKSHEET.md` | Semua 12 worksheet dan checklist | Complete |
| `RUBRIC.md` | Self-assessment semua kategori | Complete |
| `CREATION_SUMMARY.md` | Ringkasan paket ini | Complete |
| `TECHNICAL_REPORT.md` | Laporan teknis end-to-end | Complete |
| `EDA_REPORT.md` | Audit dataset dan insight | Complete |
| `EXPERIMENT_REPORT.md` | Baseline, tuning, CV, IndoBERT, errors | Complete |
| `DEPLOYMENT_AND_TESTING.md` | Runbook, endpoint, tests, security gaps | Complete |
| `PRESENTATION_GUIDE.md` | 16-slide structure, demo, script, Q&A | Complete |
| `INDEX_TASK_COMPLETION.md` | Mapping task `index.qmd` | Complete |

## Source Materials Reviewed

- Semua Markdown pada `Paparan/lab12-capstone-project`.
- Task sections pada `index.qmd`.
- Paparan `Paparan/ZKP_IoT-1.pdf` sebanyak 22 slide; halaman arsitektur, confusion matrix, dan conclusion juga ditinjau secara visual.
- Root README dan peta kode.
- Dataset CSV dan notebook training.
- Metadata/config/tokenizer/model artifact.
- Backend FastAPI, auth, ZKP, STT, autocorrect, classifier, policy, repositories, tests.
- Firmware ESP32-S3 dan dokumentasi frontend.
- Dependency list, `.gitignore`, git status, dan ketersediaan Docker.

## Verification Performed

### Dataset

- 54.656 rows × 3 columns.
- Missing=0, empty text=0, full duplicates=0.
- Normal=28.058; Emergency=26.598.
- 13 conflicting duplicate texts.
- Split replicated: 43.724/5.466/5.466.
- Text overlap: train-validation=2; train-test=1.

### Experiments

- Dummy, Logistic Regression, LinearSVC, MultinomialNB.
- LinearSVC tuning for four C values.
- Five-fold Stratified CV.
- Held-out test comparison with IndoBERT.
- IndoBERT smoke test and warmed CPU latency microbenchmark.

### Tests

Full test suite result: **34 passed in 42.76 seconds**.

## Key Corrections Incorporated

1. ZKP dijelaskan hanya sebagai proof of knowledge/device identity, bukan jaminan kerahasiaan/integritas audio.
2. Noise, masker, replay, fake device, network loss, dan alarm latency ditandai belum diuji.
3. Klaim real-time dibatasi: sistem aktif memproses chunk 3 detik, belum true streaming.
4. Accuracy model tidak disamakan dengan end-to-end system performance.
5. Docker dan missing endpoint tidak ditandai seolah selesai.
6. Credential firmware dan placeholder test dicatat sebagai remediation penting.
7. Konflik label dan inference/training max-length mismatch ditemukan dan didokumentasikan.

## Deliverable Quality Notes

- Tidak ada placeholder kosong; bagian yang tidak memiliki bukti ditulis “belum diuji/tersedia”.
- Identitas mahasiswa dicantumkan pada dokumen utama.
- Angka dihitung dari data/metadata atau diturunkan dari confusion matrix.
- File asli di `lab12-capstone-project` tetap tidak berubah.
- Dokumen dapat dijadikan sumber isi laporan/PPT, tetapi final formatting institusi dan approval dosen tetap perlu dilakukan.

## Remaining Actions

- Hapus dan rotasi credential firmware.
- Guard/hapus `AUDIO_PLACEHOLDER` production path.
- Bersihkan konflik label dan retrain.
- Tambah IndoBERT tuning/curves/attribution.
- Implementasikan Docker dan CI.
- Jalankan real audio, noise, mask, replay, fake device, network loss, latency, load, dan soak tests.
- Latih presentasi tiga kali dan simpan video demo cadangan.

## Completion Statement

Seluruh jawaban Markdown yang diminta Lab 12 telah dibuat, dan deliverable tambahan yang diwajibkan `index.qmd` juga disediakan. “Complete” pada paket dokumentasi berarti dokumennya telah diisi; bukan berarti semua production gate proyek sudah terpenuhi.

