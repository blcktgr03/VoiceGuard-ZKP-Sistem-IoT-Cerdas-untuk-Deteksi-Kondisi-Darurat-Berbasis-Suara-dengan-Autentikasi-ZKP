# Jawaban Lab 12 Capstone Project — VoiceGuard-ZKP

**Nama:** Muhamad Umar Nugroho  
**NPM:** 2322101943  
**Kelas:** III RPKK  
**Tahun akademik:** 2025/2026  
**Tanggal verifikasi dokumentasi:** 4 Agustus 2026

## Ringkasan

Folder ini berisi jawaban lengkap Lab 12 Capstone Project untuk **VoiceGuard-ZKP**, yaitu prototipe sistem IoT yang menangkap suara pekerja, mengautentikasi perangkat dengan protokol Schnorr Zero-Knowledge Proof, mentranskripsikan audio memakai faster-whisper, mengklasifikasikan teks sebagai `Normal` atau `Emergency` memakai IndoBERT dan aturan kata darurat, lalu menampilkan perangkat, lokasi, transkrip, serta status pada dashboard.

Dokumentasi disusun dari tiga kelompok bukti:

1. Paparan proyek [`ZKP_IoT-1.pdf`](../ZKP_IoT-1.pdf).
2. Kode, dataset, model, firmware, pengujian, dan dokumentasi pada seluruh folder proyek `machine_learning`.
3. Verifikasi ulang pada 4 Agustus 2026, meliputi statistik dataset, eksperimen baseline, 5-fold cross-validation, smoke test IndoBERT, dan seluruh unit test.

## Identitas proyek

| Atribut | Nilai |
|---|---|
| Judul | VoiceGuard-ZKP: Sistem IoT Cerdas untuk Deteksi Kondisi Darurat Berbasis Suara dengan Autentikasi Zero-Knowledge Proof |
| Domain | Natural Language Processing, speech processing, IoT, dan keamanan perangkat |
| Tipe masalah ML | Klasifikasi teks biner: `Normal` (0) dan `Emergency` (1) |
| Input operasional | Audio WAV mono 16-bit, 16 kHz, chunk 3 detik |
| Output | Transkrip, label, confidence, identitas/lokasi perangkat, notifikasi, dan status buzzer/dashboard |
| Model utama | Full fine-tuning `indobenchmark/indobert-base-p1` |
| STT | faster-whisper Small, bahasa Indonesia |
| Backend | FastAPI + SQLite/SQLAlchemy |
| Perangkat | ESP32-S3 + INMP441 + LED + buzzer |

## Daftar dokumen

| Dokumen | Isi |
|---|---|
| [`PROJECT_PROPOSAL_TEMPLATE.md`](PROJECT_PROPOSAL_TEMPLATE.md) | Proposal lengkap: masalah, SMART objective, ruang lingkup, metrik, jadwal, risiko, dan deliverable |
| [`WORKSHEET.md`](WORKSHEET.md) | Jawaban 12 worksheet Lab 12 beserta refleksi dan checklist aktual |
| [`MODEL_CARD_TEMPLATE.md`](MODEL_CARD_TEMPLATE.md) | Model card IndoBERT dan batas penggunaan sistem hibrida |
| [`RUBRIC.md`](RUBRIC.md) | Self-assessment berbasis bukti terhadap seluruh rubrik 100 poin |
| [`CREATION_SUMMARY.md`](CREATION_SUMMARY.md) | Ringkasan semua keluaran dan status penyelesaiannya |
| [`TECHNICAL_REPORT.md`](TECHNICAL_REPORT.md) | Laporan teknis lengkap dari perumusan masalah sampai pengembangan |
| [`EDA_REPORT.md`](EDA_REPORT.md) | Audit data, distribusi kelas, panjang teks, konflik label, dan implikasi |
| [`EXPERIMENT_REPORT.md`](EXPERIMENT_REPORT.md) | Baseline, tuning, cross-validation, hasil IndoBERT, dan error analysis |
| [`DEPLOYMENT_AND_TESTING.md`](DEPLOYMENT_AND_TESTING.md) | Arsitektur deployment, endpoint, cara menjalankan, pengujian, keamanan, dan gap produksi |
| [`PRESENTATION_GUIDE.md`](PRESENTATION_GUIDE.md) | Struktur 16 slide, alur demo, narasi, dan jawaban pertanyaan penguji |
| [`INDEX_TASK_COMPLETION.md`](INDEX_TASK_COMPLETION.md) | Pemetaan TASK 1.1–5.2 pada `index.qmd` ke bukti jawaban |

## Hasil utama yang telah diverifikasi

### Data

- Dataset final berisi **54.656 baris × 3 kolom** (`text`, `label`, `label_name`).
- Kelas Normal: **28.058 (51,3356%)**; Emergency: **26.598 (48,6644%)**.
- Nilai kosong: **0**; baris duplikat penuh: **0**; teks kosong: **0**.
- Terdapat **13 teks berulang** yang masing-masing muncul dengan label Normal dan Emergency. Ini adalah konflik label yang harus dibersihkan.
- Pembagian aktual dengan `random_state=42` dan stratifikasi: train **43.724**, validation **5.466**, test **5.466**.

### Model final IndoBERT pada test set

| Metrik | Nilai |
|---|---:|
| Accuracy | 90,61% |
| Precision Emergency | 92,25% |
| Recall Emergency | 88,12% |
| F1 Emergency | 90,14% |
| F1 macro | 90,59% |
| Balanced accuracy | 90,55% |
| MCC | 0,8127 |

Confusion matrix: TN=2.609, FP=197, FN=316, TP=2.344. Sebanyak **61,60% dari seluruh kesalahan merupakan false negative**, sehingga peningkatan recall Emergency lebih penting daripada sekadar menaikkan accuracy.

### Verifikasi implementasi

- **34/34 automated tests lulus** dalam 42,76 detik.
- Model IndoBERT tersimpan lokal sekitar **498,51 MB**; model faster-whisper Small sekitar **486,22 MB**.
- Inferensi IndoBERT setelah warm-up pada CPU: rata-rata **50,57 ms** untuk 10 input lokal. Angka ini hanya latency komponen klasifikasi, bukan latency audio-ke-alarm.
- Dockerfile, batch prediction endpoint, `/info`, pengujian kebisingan industri, uji replay, uji kehilangan jaringan, dan pengukuran end-to-end latency **belum tersedia**.

## Status bukti

Label berikut digunakan di seluruh dokumen:

- **Terverifikasi:** dibuktikan oleh file, penghitungan ulang, atau test yang dijalankan.
- **Terdokumentasi:** dinyatakan dalam paparan/README, tetapi belum memiliki pengujian empiris lengkap.
- **Belum diuji:** implementasi atau target belum memiliki bukti yang cukup.
- **Rencana:** saran pengembangan, bukan hasil proyek saat ini.

## Cara menjalankan proyek

Dari root `machine_learning`:

```powershell
& "$env:USERPROFILE\miniconda3\envs\tf-new\python.exe" -m pip install -r requirements.txt
& "$env:USERPROFILE\miniconda3\envs\tf-new\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Kemudian buka:

- Dashboard: `http://localhost:8000/dashboard`
- Dokumentasi API: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

Firmware aktif berada pada `frontend/firmware/esp32_inmp441/esp32_inmp441_emergency_detector/`. Kredensial jaringan dan alamat server pada firmware wajib dipindahkan dari source code sebelum penggunaan di luar demo.

## Pernyataan batas klaim

VoiceGuard-ZKP adalah **prototipe pendukung peringatan**, bukan perangkat keselamatan bersertifikasi dan bukan pengganti petugas, prosedur K3, tombol darurat, maupun layanan medis. ZKP pada proyek membuktikan pengetahuan secret perangkat; ZKP tidak otomatis menjamin kerahasiaan atau integritas stream audio. TLS, pengikatan pesan audio, anti-replay, parameter kriptografi produksi, dan pengujian lapangan tetap diperlukan.

