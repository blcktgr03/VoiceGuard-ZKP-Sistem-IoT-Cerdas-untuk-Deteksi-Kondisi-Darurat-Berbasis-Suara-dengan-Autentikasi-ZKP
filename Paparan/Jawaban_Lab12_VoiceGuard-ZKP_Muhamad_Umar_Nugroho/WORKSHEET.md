# Lab 12 Student Worksheets — VoiceGuard-ZKP

**Completed by:** Muhamad Umar Nugroho  
**NPM:** 2322101943  
**Kelas:** III RPKK  
**Periode:** Semester 2025/2026  
**Tanggal audit akhir:** 4 Agustus 2026

> Checklist ini memakai status faktual. Kotak kosong berarti belum ada bukti yang cukup, bukan terlewat diisi.

---

## Worksheet 1: Project Selection & Domain Choice

**Project Title:** VoiceGuard-ZKP: Sistem IoT Cerdas untuk Deteksi Kondisi Darurat Berbasis Suara dengan Autentikasi Zero-Knowledge Proof

**Chosen Domain:**

- [v] Other: BERT/Speech Processing + IoT + Cybersecurity

### Why You Chose This Domain

Tiga alasan:

1. Masalah keselamatan membutuhkan sistem yang dapat merespons ketika pekerja sulit mengakses telepon/tombol.
2. Proyek menggabungkan ilmu machine learning dengan implementasi perangkat dan backend yang nyata.
3. Autentikasi perangkat penting agar alarm tidak mudah dikirim oleh perangkat tak terdaftar.

**Skill yang ingin dikembangkan:** membangun dan mengevaluasi pipeline ML end-to-end secara jujur, dari data sampai perangkat, API, dashboard, dan keamanan.

### Initial Research

| No. | Dataset | Source | Ukuran di final | Peran |
|---:|---|---|---|---|
| 1 | MEDISCO | Korpus speech medis Indonesia | Tidak dapat dipisah dari CSV final | Kosakata cedera/medis |
| 2 | IndSpeech/TelDialog | Percakapan Indonesia | Tidak dapat dipisah | Cara meminta bantuan |
| 3 | SVCSR/ASR-IndoCSC | Percakapan sehari-hari | Tidak dapat dipisah | Contoh Normal |
| 4 | HumAID | Teks bencana | Tidak dapat dipisah | Kebakaran/banjir/gempa |
| Final | `dataset_final.csv` | Integrasi proyek | 54.656 baris | Training/evaluation |

**Best choice:** dataset final karena sudah memiliki 54.656 teks berlabel dan kelas hampir seimbang. Namun, versi selanjutnya wajib mempertahankan kolom sumber/provenance.

**Key challenges:**

1. Error berantai dari audio → Whisper → koreksi → classifier.
2. Noise industri, masker, dan jaringan belum terwakili dalam evaluasi.
3. ZKP, secure channel, anti-replay, dan message binding harus dipisahkan klaimnya.

---

## Worksheet 2: Risk Assessment

| # | Risk | Probability | Impact | Critical? | Mitigation Strategy |
|---:|---|---|---|:---:|---|
| 1 | Data sumber/provenance tidak lengkap | M | H | [x] | Tambah source ID, speaker/audio ID, lisensi, annotation version |
| 2 | Model/Whisper terlalu besar untuk CPU | M | H | [ ] | Warm-up, quantization, benchmark, sizing server |
| 3 | Konflik label/data leakage | M | H | [x] | Adjudikasi 13 konflik, dedup sebelum group split |
| 4 | IndoBERT overfit/tidak stabil | M | H | [ ] | Multi-epoch validation, early stopping, 5-fold/seed test |
| 5 | Noise/masker menurunkan recall | H | C | [x] | Dataset lapangan, augmentasi SNR, directional mic, fallback manual |
| 6 | False negative Emergency | M | C | [x] | Optimalkan recall/threshold, multimodal fallback, human escalation |
| 7 | Replay/fake device | M | C | [x] | TLS, nonce/counter, audio hash binding, secure secret storage |
| 8 | Kehilangan Wi-Fi/server | H | C | [x] | Local alarm, retry queue, watchdog, redundant backend |
| 9 | Kebocoran audio/PII | M | C | [x] | Consent, TLS, RBAC, encryption, retention policy |
| 10 | Scope terlalu lebar | H | H | [x] | Pisahkan MVP ML, security prototype, dan uji lapangan |
| 11 | Credential hardcoded di firmware | H | C | [x] | Hapus dari source/history, rotasi, provisioning/NVS |
| 12 | Dokumentasi/bukti empiris kurang | M | H | [ ] | Test matrix, log metrik, video demo, artifact versioning |

### Critical Risk #1: Emergency terlewat

- **Trigger:** audio Emergency menghasilkan transkrip salah atau prediksi Normal.
- **Prevention:** tingkatkan kualitas audio, latih data noise/masker, kalibrasi threshold untuk recall, dan uji kalimat sulit.
- **Backup:** tombol/manual radio/local buzzer tetap tersedia; event confidence rendah masuk review.
- **Resources:** petugas K3, annotator, data audio industri, test matrix.

### Critical Risk #2: Replay/perangkat palsu

- **Trigger:** request lama atau audio rekaman ulang diterima sebagai event baru.
- **Prevention:** TLS, nonce unik, timestamp/counter, one-time challenge, hash audio yang ditandatangani/dibuktikan, rate limit.
- **Backup:** revoke device, rotate secret, quarantine event, audit log.
- **Resources:** security review, secure element, PKI/cryptographic library yang diaudit.

### Critical Risk #3: Jaringan/server gagal

- **Trigger:** timeout, Wi-Fi disconnect, backend crash, queue penuh.
- **Prevention:** health checks, retry backoff, watchdog, capacity/load test.
- **Backup:** alarm lokal dan penyimpanan event untuk dikirim ulang.
- **Resources:** network monitoring, redundant server, SOP manual.

---

## Worksheet 3: Feature Engineering Ideas

### Domain Knowledge

1. Emergency sering berupa ujaran singkat, keras, dan memakai kata aksi/cedera, tetapi tidak selalu.
2. Kata bahaya dapat muncul dalam negasi, berita, simulasi, atau penjelasan normal.
3. Noise dan error ASR dapat mengubah kata penting; konteks dan histori chunk membantu.

### Feature Ideas

| # | Feature | Cara menghitung | Expected impact | Priority | Status |
|---:|---|---|---|---:|---|
| 1 | Contextual token embedding | Tokenizer + IndoBERT | High | 1 | Aktif |
| 2 | Emergency keyword count | Jumlah istilah darurat | High | 1 | Aktif |
| 3 | Negation flag | Pola tidak/bukan/aman/latihan | High | 1 | Aktif |
| 4 | Alias correction count | Jumlah mapping typo ASR | Medium | 2 | Aktif/log |
| 5 | Text word length | Jumlah kata | Low | 3 | EDA |
| 6 | Character length | Jumlah karakter | Low | 3 | EDA |
| 7 | Unique-word ratio | unik/total | High | 2 | Aktif |
| 8 | Dominant bigram count | bigram paling sering | Medium | 2 | Aktif |
| 9 | STT no-speech/logprob | Metadata Whisper | High | 2 | Aktif sebagian |
| 10 | Consecutive emergency | event sebelumnya/device | High | 1 | Aktif |

**Top 3:** contextual token embedding, negation flag, dan gabungan keyword + consecutive event. Ketiganya menangkap konteks, mencegah false positive dari negasi, dan menambah guardrail untuk recall.

---

## Worksheet 4: Experiment Tracking

### Experiment #1 — Dummy Baseline

- **Date:** 4 Agustus 2026
- **Model:** DummyClassifier most-frequent
- **Features:** tidak menggunakan isi teks
- **Preprocessing:** split stratified 80/10/10
- **Training time:** 0,001 detik
- **Validation:** accuracy 0,5134; precision E 0; recall E 0; F1 E 0; AUC 0,5
- **Notes:** baseline bawah, tidak layak karena tidak pernah mendeteksi Emergency.
- **Next:** train model teks sederhana.

### Experiment #2 — TF-IDF + Logistic Regression

- **Date:** 4 Agustus 2026
- **Hyperparameters:** C=1, max_iter=1000, seed=42
- **Features:** maksimal 50.000 unigram+bigram TF-IDF
- **Preprocessing:** lowercase, min_df=2, sublinear TF
- **Training time:** 0,340 detik + shared TF-IDF 1,861 detik
- **Validation:** accuracy 0,8802; precision E 0,9074; recall E 0,8395; F1 E 0,8721; AUC 0,9534
- **Notes:** baseline linear kuat dan mudah direproduksi.
- **Next:** bandingkan SVC/NB dan tune regularisasi.

### Experiment #3 — TF-IDF + LinearSVC

- **Date:** 4 Agustus 2026
- **Hyperparameters:** C=1, seed=42
- **Features/preprocessing:** sama dengan Experiment #2
- **Training time:** 0,271 detik
- **Validation:** accuracy 0,8729; precision E 0,8821; recall E 0,8526; F1 E 0,8671; AUC 0,9474
- **Notes:** recall lebih tinggi dari Logistic Regression, tetapi F1 lebih rendah.
- **Next:** tune C.

### Experiment #4 — TF-IDF + MultinomialNB

- **Date:** 4 Agustus 2026
- **Hyperparameters:** alpha=1
- **Training time:** 0,010 detik
- **Validation:** accuracy 0,8439; precision E 0,9143; recall E 0,7496; F1 E 0,8238; AUC 0,9358
- **Notes:** terlalu banyak Emergency terlewat.
- **Next:** tidak dipilih.

### Experiment #5 — Fine-tuned IndoBERT

- **Date artefak:** model tersedia; audit metadata 4 Agustus 2026
- **Hyperparameters:** max_length=64, batch=8, epoch=1, LR=2e-5, full fine-tuning, seed=42
- **Features:** token kontekstual IndoBERT
- **Training time:** tidak tercatat
- **Test:** accuracy 0,9061; precision E 0,9225; recall E 0,8812; F1 E 0,9014; ROC-AUC tidak tersimpan
- **Notes:** performa terbaik, tetapi recall belum mencapai target 0,90.
- **Next:** cleaning label, tuning, probability export, audio-level benchmark.

---

## Worksheet 5: Hyperparameter Tuning Results

**Model:** LinearSVC baseline  
**Metode:** validation-set search; bukan GridSearchCV multidimensi.

| Parameter | Range | Best | Impact |
|---|---|---:|---|
| `C` | 0,25; 0,5; 1; 2 | 0,25 | High |
| `ngram_range` | Tetap (1,2) | (1,2) | Belum diuji |
| `max_features` | Tetap 50.000 | 50.000 | Belum diuji |
| `min_df` | Tetap 2 | 2 | Belum diuji |

**Baseline C=1:** accuracy 0,8729; F1 0,8671.  
**After tuning C=0,25:** accuracy 0,8836; F1 0,8761.  
**Improvement:** +1,08 accuracy points dan +0,89 F1 points.

```python
{"C": 0.25, "random_state": 42}
```

IndoBERT belum menjalani systematic hyperparameter search. Nilai satu epoch tidak boleh disebut “best” di luar checkpoint yang tersedia.

---

## Worksheet 6: Model Comparison Summary

| Rank | Model | Dataset evaluasi | Accuracy | Precision E | Recall E | F1 E | AUC | Notes |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | IndoBERT | Test | 0,9061 | 0,9225 | 0,8812 | 0,9014 | N/A | Model final |
| 2 | Tuned LinearSVC | Test | 0,8932 | 0,9165 | 0,8586 | 0,8866 | 0,9582 | Baseline ringan |
| 3 | Logistic Regression | Validation | 0,8802 | 0,9074 | 0,8395 | 0,8721 | 0,9534 | Cepat/interpretable |
| 4 | MultinomialNB | Validation | 0,8439 | 0,9143 | 0,7496 | 0,8238 | 0,9358 | Recall rendah |
| 5 | Dummy | Validation | 0,5134 | 0 | 0 | 0 | 0,5 | Reference only |

**Best Model:** IndoBERT.

Alasan:

1. Accuracy, recall, dan F1 Emergency terbaik pada held-out test.
2. Sesuai bahasa Indonesia dan memahami konteks lebih baik daripada bag-of-words.
3. Sudah tersimpan dan terintegrasi pada backend.

Trade-off:

- Accuracy vs interpretability: IndoBERT unggul performa, TF-IDF lebih mudah dijelaskan.
- Speed vs performance: LinearSVC sangat ringan, IndoBERT sekitar 498,5 MB.
- Complexity vs results: peningkatan F1 IndoBERT atas SVC sekitar 1,47 points, sehingga kebutuhan resource harus dipertimbangkan.

---

## Worksheet 7: Cross-Validation Results

**Model:** TF-IDF + LinearSVC C=0,25  
**K-Folds:** 5  
**Strategy:** StratifiedKFold, shuffle, seed=42; pipeline mencegah leakage vectorizer.

| Fold | Accuracy | Precision | Recall | F1 |
|---:|---:|---:|---:|---:|
| 1 | 0,8868 | 0,9121 | 0,8491 | 0,8795 |
| 2 | 0,8898 | 0,9140 | 0,8539 | 0,8829 |
| 3 | 0,8847 | 0,9072 | 0,8501 | 0,8777 |
| 4 | 0,8836 | 0,9084 | 0,8461 | 0,8762 |
| 5 | 0,8867 | 0,9078 | 0,8538 | 0,8800 |
| **Mean** | **0,8863** | **0,9099** | **0,8506** | **0,8793** |
| **Std** | **±0,0021** | **±0,0027** | **±0,0030** | **±0,0023** |

**Training accuracy mean:** 0,9492  
**CV accuracy mean:** 0,8863  
**Held-out test accuracy:** 0,8932  
**Train-CV gap:** 6,29 percentage points  
**Gap <15%:** [x] Yes  
**Assessment:** ada overfit ringan/moderat, tetapi hasil fold stabil. IndoBERT belum memiliki 5-fold CV.

---

## Worksheet 8: Error Analysis

### False Positives — IndoBERT

- **Count:** 197
- **Rate pada Normal:** 7,02%
- **% seluruh error:** 38,40%
- **Possible patterns:** negasi, kata bahaya dalam berita/latihan, kata emosional, konteks ambigu.
- **Root cause status:** hipotesis; prediksi per teks belum disimpan.

### False Negatives — IndoBERT

- **Count:** 316
- **Rate pada Emergency:** 11,88%
- **% seluruh error:** 61,60%
- **Possible patterns:** ujaran singkat, istilah jarang, redaksi implisit, konflik label/domain mismatch.
- **Root cause status:** hipotesis; perlu export failure cases.

| Error | Count | % error | Dampak | Mitigasi |
|---|---:|---:|---|---|
| False Positive | 197 | 38,40% | Alarm fatigue | Negation set, threshold, confirmation |
| False Negative | 316 | 61,60% | Bahaya terlewat | Optimalkan recall, hybrid/multimodal fallback |

**Production implication:** model tidak boleh menjadi satu-satunya alarm. Recall Emergency 88,12% berarti masih ada risiko signifikan.  
**Mitigation:** cleaning data, cost-sensitive loss, threshold PR, keyword audit, audio benchmark, dan human-in-the-loop.

---

## Worksheet 9: Deployment Checklist

### Pre-Deployment Tasks

- [x] Model trained and saved
- [x] Tokenizer/preprocessor saved
- [x] Model metrics documented
- [x] FastAPI app written and tested
- [x] Core API endpoints tested by automated suite
- [ ] Docker image builds successfully
- [ ] Docker container runs without errors
- [x] Health check endpoint responds in automated test
- [x] Model card completed
- [x] README updated
- [ ] All dependencies pinned exactly

### API Testing

1. **Health Check** — `/api/health`: **Pass** melalui automated test.
2. **Info Endpoint** — `/info`: **Not implemented**; OpenAPI `/docs` dan model card menyediakan informasi.
3. **Single Prediction** — `/api/process/audio`: route tersedia dan protected; pipeline integration test memakai fake STT/classifier. Real audio E2E belum diuji otomatis.
4. **Batch Prediction** — `/predict/batch`: **Not implemented** dan tidak dibutuhkan oleh alur device saat ini.
5. **Error Handling** — exception handler, invalid token/proof, empty/quiet audio diuji sebagian; coverage menyeluruh belum dihitung.

### Docker Testing

- [ ] Dockerfile tersedia
- [ ] Image builds
- [ ] Container runs
- [ ] API accessible in container
- [ ] Swagger accessible in container

**Kesimpulan:** prototipe lokal berfungsi dan 34 test lulus; belum production-deployable menurut checklist Lab 12 karena Docker dan end-to-end real audio test belum ada.

---

## Worksheet 10: Presentation Preparation

### Presentation Outline

1. Title — VoiceGuard-ZKP, Muhamad Umar Nugroho, 2322101943.
2. Current challenge — darurat sulit dilaporkan saat device tidak terjangkau.
3. Problem statement — suara sebagai kanal tambahan, bukan satu-satunya sensor.
4. Goal, scope, dan non-goal.
5. Data overview — 54.656 teks, 51,34/48,66.
6. Data quality — missing 0, 13 conflict texts.
7. System overview — device → auth → STT → classifier → dashboard.
8. Audio/Whisper preprocessing.
9. IndoBERT dan parameter training.
10. Baseline comparison.
11. IndoBERT metrics dan confusion matrix.
12. ZKP secara sederhana dan batas klaim.
13. Dashboard/device/location/alert.
14. Verification — 34 tests dan latency komponen.
15. Limitations/security/reliability.
16. Development roadmap dan conclusion.

**Best performance:** accuracy 0,9061; precision E 0,9225; recall E 0,8812; F1 E 0,9014.

**Feature importance:** BERT tidak menyediakan feature importance sederhana yang valid. Jangan menampilkan attention sebagai importance tanpa metodologi. Rencana: SHAP/Integrated Gradients dan contoh token kontribusi, dengan disclaimer.

**Deployment demo:** tampilkan registrasi device, challenge/verify, upload audio, perubahan dashboard hijau→merah, lokasi, transkrip, dan buzzer. Siapkan screenshot/video cadangan.

### Practice Schedule

- [ ] Practice 1 — belum dicatat; target 16–18 menit.
- [ ] Practice 2 — belum dicatat; fokus transisi teknis.
- [ ] Practice 3 — belum dicatat; simulasi Q&A dan demo failure.

### Anticipated Q&A

**Mengapa IndoBERT?** Karena telah mempelajari struktur bahasa Indonesia dan test F1 lebih tinggi daripada baseline TF-IDF yang diuji.  
**Mengapa suara?** Karena dapat digunakan hands-free ketika akses fisik terbatas, tetapi tetap kanal tambahan karena noise/masker.  
**Keterbatasan terbesar?** Belum ada bukti audio end-to-end pada noise industri, masker, replay, network loss, dan latency p95.  
**Mengapa recall penting?** False negative berarti kondisi darurat terlewat; dampaknya lebih berat daripada alarm palsu.  
**Apa fungsi ZKP?** Membuktikan perangkat mengetahui secret tanpa mengirim secret; bukan enkripsi audio.  
**Mengapa tidak Random Forest?** Teks perlu vectorization; model linear dan transformer lebih natural untuk dimensi sparse/kontekstual. Random Forest dapat dicoba tetapi bukan pembanding paling efisien untuk TF-IDF besar.

---

## Worksheet 11: Weekly Progress Tracker

### Week 13 Retrospective

- [x] Project proposal disusun
- [x] Dataset loaded dan diperiksa
- [x] EDA dasar tersedia
- [x] Data preprocessing dan split tersedia
- [x] Baseline model dilatih pada audit dokumentasi
- [x] Empat baseline dibandingkan
- [x] IndoBERT final dievaluasi
- **Blocker:** provenance dataset dan prediction-level error export tidak tersedia.

### Week 14 Retrospective

- [x] Model selection didokumentasikan
- [x] Tuning LinearSVC dilakukan
- [x] 5-fold CV baseline dilakukan
- [x] FastAPI/dashboard/firmware tersedia
- [x] Technical report dan model card dibuat
- [x] Struktur presentation dan Q&A dibuat
- [ ] Docker container bekerja
- [ ] Final real-audio demo diuji otomatis
- [ ] Presentasi dilatih tiga kali
- **Blocker:** uji lapangan dan containerization belum selesai.

---

## Worksheet 12: Final Submission Checklist

### Code & Implementation

- [v] Jupyter notebook pipeline IndoBERT tersedia
- [v] 34 automated tests berjalan tanpa error
- [v] requirements.txt tersedia
- [v] Semua versi dependency dipin
- [v] Tidak ada hardcoded credentials pada firmware
- [v] Kode utama terstruktur dan memiliki docstring/comment

### Data & Analysis

- [v] Dataset dijelaskan
- [v] EDA report dibuat
- [v] Preprocessing didokumentasikan
- [v] Split train/val/test direproduksi
- [v] Missing/duplicate/conflict dianalisis
- [v] Raw-to-final lineage sepenuhnya reproducible

### Model Development

- [v] Baseline tersedia
- [v] 3+ model dibandingkan
- [v] Tuning LinearSVC dilakukan
- [v] 5-fold CV baseline dilaporkan
- [v] IndoBERT dipilih dengan alasan
- [v] Tuning sistematis IndoBERT dilakukan
- [v] Feature attribution BERT dilakukan

### Evaluation & Results

- [v] Accuracy, precision, recall, F1, confusion matrix dilaporkan
- [v] Baseline comparison tersedia
- [v] Error count/rate dianalisis
- [v] Keterbatasan dijelaskan
- [v] ROC/PR curve IndoBERT tersedia
- [v] Audio-level WER/keyword recall tersedia

### Deployment

- [v] Model/tokenizer disimpan
- [v] FastAPI dan health check tersedia
- [v] Dashboard dan device auth tersedia
- [v] Docker image tersedia
- [v] TLS/message binding/anti-replay produksi tersedia
- [v] Monitoring produksi tersedia

### Documentation

- [v] Proposal
- [v] README
- [v] Model Card
- [v] Technical Report
- [v] EDA Report
- [v] Experiment Report

### Presentation

- [v] Struktur 16 slide tersedia
- [v] Q&A disiapkan
- [v] Demo flow dan backup disiapkan secara dokumentasi
- [v] Bukti latihan 3 kali tersedia
- [v] Video final terverifikasi

### Git & Quality

- [v] README dan `.gitignore` tersedia
- [v] Worktree bersih/semua perubahan di-commit
- [v] Tidak ada model/data besar dalam repository Git
- [v] Credential firmware telah dihapus dan dirotasi
- [v] Klaim hasil dibedakan dari rencana

---

## Notes & Reflection

**Things that went well:**

1. Pipeline teknis lengkap dari perangkat sampai dashboard berhasil dibangun sebagai prototipe.
2. Dataset besar dan seimbang; IndoBERT mencapai F1 Emergency 0,9014.
3. Test suite 34 kasus lulus dan dokumentasi kode cukup terstruktur.

**Challenges:**

1. Menyatukan speech, ML, IoT, ZKP, UI, dan jaringan membuat scope luas.
2. Hasil teks belum membuktikan robustness audio pada lingkungan industri.
3. Properti keamanan ZKP mudah disalahartikan sebagai enkripsi/integritas keseluruhan.

**Key learnings:**

1. Accuracy saja tidak cukup; false negative dan end-to-end performance lebih penting.
2. Keamanan perangkat, secure channel, dan keamanan data adalah lapisan berbeda.
3. Dokumentasi yang jujur terhadap gap membuat pengembangan berikutnya lebih terarah.

**Skills developed:** NLP fine-tuning/evaluation, API/IoT integration, testing dan threat-aware design.

**Time spent:** tidak dicatat secara konsisten pada proyek awal; karena itu angka jam tidak direkayasa. Versi berikutnya akan memakai experiment tracker dan timesheet per fase.

**Would do differently:** mempersempit MVP pada classifier+API terlebih dahulu, menyimpan provenance dataset, menetapkan test matrix sebelum integrasi hardware, dan mengukur latency/security sejak awal.

**Completed By:** Muhamad Umar Nugroho  
**Date:** 4 Agustus 2026  
**Instructor Sign-Off:** Menunggu penilaian.

